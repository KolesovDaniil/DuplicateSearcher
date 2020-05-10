"""Module with view functions"""

from __future__ import division
from PIL import Image

import os
import subprocess
import cv2
import shutil

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from app.database import db
from app.models import Video, VideoHash, Log

from app.exceptions import NotFoundError
from app.exceptions import ForbiddenError

MAIN_DIR = '/home/DinaKursach/'
SUBDIR = MAIN_DIR + 'pict/'


def process(id, mail=''):
    connect_to_drive(id)
    return get_table_link(mail)


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
    #try:
        filelist = []
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % parent}).GetList()
        if not file_list:
            raise ForbiddenError("Object cannot be accessed")
        for f in file_list:
            if f['mimeType'] == 'application/vnd.google-apps.folder':  # if folder
                filelist.append({"id": f['id'], "title": f['title'],
                                 "list": list_folder(f['id'], folder, drive, service)})
            elif f['mimeType'] == 'video/mp4':
                file = drive.CreateFile({'id': f['id']})
                GD_download_file(service, f['id'])
                added_video = add_video(transliterate(f["title"]).replace("_avi", ".avi"), f["alternateLink"])
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
                        for vid in os.listdir(os.path.splitext(video)[0]):
                            if '.mp4' in vid:
                                if vid == added_video.name:
                                    search_similar(added_video.id, MAIN_DIR + vid.split(".")[0] + '/')
                        delete_dir(video.split(".")[0])
        return filelist
    #except:
        raise NotFoundError("The object is not found")


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
    video_parts = partial(total_size,
                          100000000)  # I'm downloading BIG files, so 100M chunk size is fine for me
    title = transliterate(drive_file.get('title')).replace("_avi", ".avi")
    original_filename = transliterate(drive_file.get('originalFilename')).replace("_avi", ".avi")
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


def add_hash(video_id, timecode, video_hash):
    """Function to add hash to database"""

    hash = VideoHash(video_id=video_id, time_code=timecode, hash=video_hash)
    db.session.add(hash)


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
   slovar = {'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e',
      'ж':'zh','з':'z','и':'i','й':'i','к':'k','л':'l','м':'m','н':'n',
      'о':'o','п':'p','р':'r','с':'s','т':'t','у':'u','ф':'f','х':'h',
      'ц':'c','ч':'cz','ш':'sh','щ':'scz','ъ':'','ы':'y','ь':'','э':'e',
      'ю':'u','я':'ja', 'А':'A','Б':'B','В':'V','Г':'G','Д':'D','Е':'E','Ё':'E',
      'Ж':'ZH','З':'Z','И':'I','Й':'I','К':'K','Л':'L','М':'M','Н':'N',
      'О':'O','П':'P','Р':'R','С':'S','Т':'T','У':'U','Ф':'F','Х':'H',
      'Ц':'C','Ч':'CZ','Ш':'SH','Щ':'SCH','Ъ':'','Ы':'y','Ь':'','Э':'E',
      'Ю':'U','Я':'YA',',':'','?':'',' ':'_','~':'','!':'','@':'','#':'',
      '$':'','%':'','^':'','&':'','*':'','(':'',')':'','-':'','=':'','+':'',
      ':':'',';':'','<':'','>':'','\'':'','"':'','\\':'','/':'','№':'',
      '[':'',']':'','{':'','}':'','ґ':'','ї':'', 'є':'','Ґ':'g','Ї':'i',
      'Є':'e', '—':'', '.':'_'}
   for key in slovar:
      name = name.replace(key, slovar[key])
   return name


def get_table_link(mail):
    """Function to get link of GoogleSheets link"""
    pass
