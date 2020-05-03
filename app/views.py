"""Module with view functions"""

from __future__ import division
from PIL import Image

import os
import subprocess
import cv2
import shutil

from contextlib import closing
import pymysql
from pymysql.cursors import DictCursor

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

MAIN_DIR = 'C:/Users/dfkhasanova/Desktop/Учеба/NIR/script/'
SUBDIR = MAIN_DIR + 'pict/'


def connect_to_drive(dir):
    """Function to connect to Google Drive"""
    gauth = GoogleAuth()
    # Try to load saved client credentials
    gauth.LoadCredentialsFile("mycreds.txt")
    if gauth.credentials is None:
        # Authenticate if they're not there
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # Refresh them if expired
        gauth.Refresh()
    else:
        # Initialize the saved creds
        gauth.Authorize()
    # Save the current credentials to a file
    gauth.SaveCredentialsFile("mycreds.txt")
    drive = GoogleDrive(gauth)
    service = gauth.service
    list_folder(dir, SUBDIR, drive, service)


def list_folder(parent, folder, drive, service):
    """Function to get all videos"""
    filelist = []
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if f['mimeType'] == 'application/vnd.google-apps.folder':  # if folder
            filelist.append({"id": f['id'], "title": f['title'], "list": list_folder(f['id'], folder, drive, service)})
        elif f['mimeType'] == 'video/x-msvideo':
            file = drive.CreateFile({'id': f['id']})
            GD_download_file(service, f['id'])
            results = add_video(f["title"], f["alternateLink"])
            for video in os.listdir(MAIN_DIR):
                if '.avi' in video:
                    os.makedirs("pict", exist_ok=True)
                    subprocess.call(
                        ['ffmpeg', '-i', video, '-vf', "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,10)'",
                         '-vsync', '0', '-an', '-frame_pts', '1',
                         'pict/%d.jpg'])
                    os.rename(MAIN_DIR + video, SUBDIR + video)
                    os.rename(SUBDIR, MAIN_DIR + os.path.splitext(video)[0] + '/')
                    for vid in os.listdir(os.path.splitext(video)[0]):
                        if '.avi' in vid:
                            for element in results:
                                if vid == element["video_name"]:
                                    search_similar(element["id"], MAIN_DIR + vid.split(".")[0] + '/')
                    delete_dir(video.split(".")[0])
    return filelist


def partial(total_byte_len, part_size_limit):
    """Function to get parts of video"""
    video_parts = []
    for p in range(0, total_byte_len, part_size_limit):
        last = min(total_byte_len - 1, p + part_size_limit - 1)
        video_parts.append([p, last])
    return video_parts


def GD_download_file(service, file_id):
    """Function to download video"""
    drive_file = service.files().get(fileId=file_id).execute()
    download_url = drive_file.get('downloadUrl')
    total_size = int(drive_file.get('fileSize'))
    video_parts = partial(total_size, 100000000)  # I'm downloading BIG files, so 100M chunk size is fine for me
    title = drive_file.get('title')
    original_filename = drive_file.get('original_filename')
    filename = './' + original_filename
    if download_url:
        with open(filename, 'wb') as file:
            for bytes in video_parts:
                headers = {"Range": 'bytes=%s-%s' % (bytes[0], bytes[1])}
                resp, content = service._http.request(download_url, headers=headers)
                if resp.status == 206:
                    file.write(content)
                    file.flush()
                else:
                    return None
        return title, filename
    else:
        return None


def add_video(video_name, video_url):
    """Function to add video data to database"""
    with closing(pymysql.connect(
            host='localhost',
            user='dina',
            password='hsehse',
            db='miem',
            charset='utf8mb4',
            cursorclass=DictCursor
    )) as connection:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO
                video_table (video_name, video_url, video_fps)
            VALUES
                ( %(video_name)s, %(video_url)s , %(video_fps)s)
            """
            data = [{
                'video_name': video_name,
                'video_url': video_url,
                'video_fps': cv2.VideoCapture(video_name).get(cv2.CAP_PROP_FPS)
            }]

            try:
                cursor.executemany(query, data)
                connection.commit()
            except:
                connection.rollback()
                return ("Database error")

            try:
                cursor.execute("SELECT * FROM video_table WHERE video_url=%s LIMIT 1", video_url)
                results = cursor.fetchall()
                connection.commit()
                return (results)
            except:
                connection.rollback()
                return ("Database error")


def search_hash(video_id, hash_curr, filename, tolerance):
    """Function to search videos"""
    with closing(pymysql.connect(
            host='localhost',
            user='root',
            password='hsepassword',
            db='miem',
            charset='utf8mb4',
            cursorclass=DictCursor
    )) as connection:
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT * FROM hash_table WHERE video_id NOT LIKE %s", video_id)
                results = cursor.fetchall()
                connection.commit()
                for res in results:
                    if hashes_are_similar(res["hash"], hash_curr, tolerance):
                        write_logs(video_id, filename, res["video_id"], res["timecode"])
            except:
                connection.rollback()


def write_logs(video1, timecode1, video2, timecode2):
    """Function to write results of search"""
    with closing(pymysql.connect(
            host='localhost',
            user='root',
            password='hsepassword',
            db='miem',
            charset='utf8mb4',
            cursorclass=DictCursor
    )) as connection:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO
                logs (video1_id, timecode_1, video2_id, timecode_2)
            VALUES
                ( %(name1)s, %(time1)s, %(name2)s, %(time2)s )
            """
            data = [{
                'name1': video1,
                'time1': timecode1,
                'name2': video2,
                'time2': timecode2
            }]
            try:
                cursor.executemany(query, data)
                connection.commit()
            except:
                connection.rollback()


def add_hash(video_id, timecode, video_hash):
    """Function to add hash to database"""
    with closing(pymysql.connect(
            host='localhost',
            user='root',
            password='hsepassword',
            db='miem',
            charset='utf8mb4',
            cursorclass=DictCursor
    )) as connection:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO
                hash_table (video_id, timecode, hash)
            VALUES
                ( %(video_id)s, %(timecode)s, %(hash)s )
            """
            data = [{
                'video_id': video_id,
                'timecode': timecode,
                'hash': video_hash
            }]
            try:
                cursor.executemany(query, data)
                connection.commit()
            except:
                connection.rollback()


def hash_distance(left_hash, right_hash):
    """Compute the hamming distance between two hashes"""
    if len(left_hash) != len(right_hash):
        raise ValueError('Hamming distance requires two strings of equal length')

    return sum(map(lambda x: 0 if x[0] == x[1] else 1, zip(left_hash, right_hash)))


def hashes_are_similar(left_hash, right_hash, tolerance=0):
    """
    Return True if the hamming distance between
    the image hashes are less than the given tolerance.
    """
    return hash_distance(left_hash, right_hash) <= tolerance


def average_hash(image_path, hash_size=8):
    """ Compute the average hash of the given image. """
    with open(image_path, 'rb') as f:
        # Open the image, resize it and convert it to black & white.
        image = Image.open(f).resize((hash_size, hash_size), Image.ANTIALIAS).convert('L')
        pixels = list(image.getdata())

    avg = sum(pixels) / len(pixels)

    # Compute the hash based on each pixels value compared to the average.
    bits = "".join(map(lambda pixel: '1' if pixel > avg else '0', pixels))
    hashformat = "0{hashlength}x".format(hashlength=hash_size ** 2 // 4)
    return int(bits, 2).__format__(hashformat)


def distance(image_path, other_image_path):
    """ Compute the hamming distance between two images"""
    image_hash = average_hash(image_path)
    other_image_hash = average_hash(other_image_path)

    return hash_distance(image_hash, other_image_hash)


def is_look_alike(image_path, other_image_path, tolerance=0):
    image_hash = average_hash(image_path)
    other_image_hash = average_hash(other_image_path)

    return hashes_are_similar(image_hash, other_image_hash, tolerance)


def search_similar(video_id, subdir):
    for filename in os.listdir(subdir):
        if '.jpg' in filename:
            file = filename.split(".")[0]
            hash_curr = average_hash(subdir + '/' + file + ".jpg")
            search_hash(video_id, hash_curr, file, tolerance=0)
            add_hash(video_id, file, hash_curr)


def delete_dir(folder):
    """Function delete created directory"""
    shutil.rmtree(MAIN_DIR + folder, ignore_errors=True)
    print(MAIN_DIR + folder)


def get_table_link():
    """Function for getting link of GoogleSheets link"""
    pass
