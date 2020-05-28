"""Module with view functions"""

from __future__ import division

import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from app.exceptions import NotFoundError, ForbiddenError

CREDENTIALS_FILE = 'diploma-264613-8c34223b5cf0.json'


def check_access(dir):
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
    try:
        file_list = drive.ListFile({'q': "'%s' in parents and trashed=false" % dir}).GetList()
        if not file_list:
            raise ForbiddenError("Object cannot be accessed")
    except:
        raise NotFoundError("The object is not found")
    return gauth


def check_task_existing():
    pass


def create_result_table(mail):

    credentials = ServiceAccountCredentials. \
        from_json_keyfile_name(CREDENTIALS_FILE,
                               ['https://www.googleapis.com/auth/spreadsheets',
                                'https://www.googleapis.com/auth/drive'])
    http_auth = credentials.authorize(httplib2.Http())
    service = apiclient.discovery.build('sheets', 'v4', http=http_auth)

    spreadsheet = service.spreadsheets().create(body={
        'properties': {'title': 'Results', 'locale': 'ru_RU'},
        'sheets': [{'properties': {'sheetType': 'GRID',
                                   'sheetId': 0,
                                   'title': '1'}}]
    }).execute()
    drive_service = apiclient.discovery.build('drive', 'v3', http=http_auth)

    if mail:
        drive_service.permissions().create(
            fileId=spreadsheet['spreadsheetId'],
            body={'type': 'user', 'role': 'writer', 'emailAddress': mail},
            fields='id'
        ).execute()
    else:
        drive_service.permissions().create(
            fileId=spreadsheet['spreadsheetId'],
            body={'type': 'anyone', 'role': 'writer'},
            fields='id'
        ).execute()
    return service, spreadsheet['spreadsheetId']


def get_task_status():
    pass
