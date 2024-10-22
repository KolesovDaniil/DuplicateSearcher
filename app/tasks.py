"""Module with view functions"""

from __future__ import division
from PIL import Image

import os
import subprocess
import cv2
import shutil
from pydrive.drive import GoogleDrive

from app.database import db

from app.models import Video, VideoHash, Log
from app.config import Config

MAIN_DIR = '/home/DinaKursach/'
SUBDIR = MAIN_DIR + 'pict/'


def process(id, gauth, service, spreadsheet_id):
    list_folder(id, SUBDIR, gauth, service, spreadsheet_id)


def partial(total_byte_len, part_size_limit):
    """Function to get parts of video"""
    video_parts = []
    for p in range(0, total_byte_len, part_size_limit):
        last = min(total_byte_len - 1, p + part_size_limit - 1)
        video_parts.append([p, last])
    return video_parts


def list_folder(parent, folder, gauth, spreadsheet_service, spreadsheet_id):
    """Function to get all videos"""
    drive = GoogleDrive(gauth)
    service = gauth.service
    filelist = []
    file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
    for f in file_list:
        if f['mimeType'] == 'application/vnd.google-apps.folder':  # if folder
            filelist.append({"id": f['id'], "title": f['title'],
                             "list": list_folder(f['id'], folder, gauth, spreadsheet_service,
                                                 spreadsheet_id)})
        elif f['mimeType'] == 'video/mp4':
            file = drive.CreateFile({'id': f['id']})
            GD_download_file(service, f['id'])
            added_video = add_video(transliterate(f["title"]) \
                                    .replace("_mp4", ".mp4"), f["alternateLink"])
            for video in os.listdir(MAIN_DIR):
                if '.mp4' in video:
                    os.makedirs("pict", exist_ok=True)
                    subprocess.call(
                        ['ffmpeg', '-i', video, '-vf',
                         "select='isnan(prev_selected_t)+gte(t-prev_selected_t\,10)'",
                         '-vsync', '0', '-an', '-frame_pts', '1',
                         'pict/%d.jpg'])
                    os.rename(MAIN_DIR + video, SUBDIR + video)
                    os.rename(SUBDIR, MAIN_DIR + os.path.splitext(video)[0] + '/')
                    search_similar(added_video.id,
                                   MAIN_DIR + added_video.name.split(".")[0] + '/')
                    delete_dir(video.split(".")[0])
                    insert_results(spreadsheet_service, spreadsheet_id)

    return filelist


def GD_download_file(service, file_id):
    """Function to download video"""
    drive_file = service.files().get(fileId=file_id).execute()
    download_url = drive_file.get('downloadUrl')
    total_size = int(drive_file.get('fileSize'))
    video_parts = partial(total_size,
                          100000000)
    title = transliterate(drive_file.get('title')).replace("_mp4", ".mp4")
    original_filename = transliterate(drive_file.get('originalFilename')).replace("_mp4", ".mp4")
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


def add_video(video_name, video_url) -> Video:
    """Function to add video data to database"""

    new_video = Video(name=video_name, url=video_url,
                      fps=cv2.VideoCapture(video_name).get(cv2.CAP_PROP_FPS))

    db.session.add(new_video)
    db.session.commit()

    return new_video


def search_hash(video_id, hash_curr, filename, tolerance):
    """Function to search videos"""

    results = db.session.query(VideoHash).filter(VideoHash.video_id != video_id).all()
    for res in results:
        if hashes_are_similar(res.hash, hash_curr, tolerance):
            write_logs(video_id, filename, res.video_id, res.time_code)


def write_logs(video1, timecode1, video2, timecode2):
    """Function to write results of search"""

    log = Log(video1_id=video1, time_code1=timecode1, video2_id=video2, time_code2=timecode2)
    db.session.add(log)
    db.session.commit()


def add_hash(video_id, timecode, video_hash):
    """Function to add hash to database"""

    hash = VideoHash(video_id=video_id, time_code=timecode, hash=video_hash)
    db.session.add(hash)
    db.session.commit()


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


def transliterate(name):
    slovar = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
              'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'i', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n',
              'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h',
              'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e',
              'ю': 'u', 'я': 'ja', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
              'Ё': 'E',
              'Ж': 'ZH', 'З': 'Z', 'И': 'I', 'Й': 'I', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
              'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H',
              'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': '', 'Э': 'E',
              'Ю': 'U', 'Я': 'YA', ',': '', '?': '', ' ': '_', '~': '', '!': '', '@': '', '#': '',
              '$': '', '%': '', '^': '', '&': '', '*': '', '(': '', ')': '', '-': '', '=': '',
              '+': '',
              ':': '', ';': '', '<': '', '>': '', '\'': '', '"': '', '\\': '', '/': '', '№': '',
              '[': '', ']': '', '{': '', '}': '', 'ґ': '', 'ї': '', 'є': '', 'Ґ': 'g', 'Ї': 'i',
              'Є': 'e', '—': '', '.': '_'}

    for key in slovar:
        name = name.replace(key, slovar[key])

    return name


def insert_results(service, spreadsheet_id):
    """Function to get link of GoogleSheets link"""

    engine = db.create_engine(Config().SQLALCHEMY_DATABASE_URI, {})
    query = engine.connect().execute("""SELECT 
    (SELECT url FROM video WHERE id=video1_id) AS video_1, 
    (SELECT url FROM video WHERE id=video2_id) AS video_2, 
    (SELECT count() FROM video_hash WHERE video_id=video1_id)
    /count(video2_id) * 100 as video_similarity 
        FROM log 
        GROUP BY video1_id, video2_id 
        HAVING video_similarity<100
    UNION
    SELECT 
    (SELECT url FROM video WHERE id=video1_id) AS video_1, 
    (SELECT url FROM video WHERE id=video2_id) AS video_2, 
    count(video2_id)/
    (SELECT count() FROM video_hash WHERE video_id=video1_id) * 100 as video_similarity 
        FROM log 
        GROUP BY video1_id, video2_id 
        HAVING video_similarity<100
    UNION
    SELECT 
    (SELECT url FROM video WHERE id=video1_id) AS video_1, 
    (SELECT url FROM video WHERE id=video2_id) AS video_2, 
    count(video2_id)/
    (SELECT count() FROM video_hash WHERE video_id=video1_id) * 100 as video_similarity 
        FROM log 
        GROUP BY video1_id, video2_id 
        HAVING video_similarity=100;""")

    results = [list(row) for row in query]
    result = [["video1_url", "video1_url", "similarity"]]
    result.extend(results)
    table = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id, body={
        "valueInputOption": "USER_ENTERED",
        "data": [
            {"range": "1",
             "majorDimension": "ROWS",
             "values": result}
        ]
    }).execute()
