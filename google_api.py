"""
The module is designed to work with the Google APi.
Getting information about videos from a playlist from YouTube
Google Sheets Tables
"""

from __future__ import print_function

import json
import os.path
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import requests


# The Class gets information about videos in playlist
class YouTube:

    def __init__(self):
        self.DEVELOPER_KEY = 'AIzaSyCRBXYU_iyqEFu3MHlkJsvreJiSFfnM2lY'
        self.max_result = 100
        self.playlist_id = 'PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa'

    # YouTube Search generates a dictionary of video titles in the key and a link to it in the value.
    def youtube_search(self):
        request_link = f'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&' \
                       f'maxResults={self.max_result}&' \
                       f'playlistId={self.playlist_id}&key={self.DEVELOPER_KEY}'

        response = requests.get(request_link)
        videos_info = json.loads(response.text)['items']

        # Forming a link to view a video in a playlist
        pattetn_link = 'https://www.youtube.com/watch?v='

        # Result
        videos = {}

        for video_info in videos_info:
            videos[video_info['snippet']['title']] = pattetn_link + video_info['snippet']['resourceId']['videoId'] + \
                                                     '&list=PLDyJYA6aTY1lPWXBPk0gw6gR8fEtPDGKa&'

        return videos


#   The class is necessary for working with the table (writing and reading information)
class GoogleSheet:

    # __init__ this is an example from the Google Sheets API documentation
    SPREADSHEET_ID = '1eQpvNujPKjw_q2N-zjli2IcZO0K0YwIJJwhjXTipeEo'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    service = None

    def __init__(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                print('flow')
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('sheets', 'v4', credentials=creds)

    def write_data(self, _range, values):
        data = [{
            'range': _range,
            'values': values
        }]
        body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }
        result = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.SPREADSHEET_ID,
                                                                  body=body).execute()

    def read_data(self, range):

        result = self.service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID, range=range).execute()
        values = result.get('values', [])

        return values


# If the file is executable, then links from the YouTube playlist are generated in the table.
# It's necessary for testing
def main():

    gs = GoogleSheet()
    videos = YouTube().youtube_search()
    data = [[title, link] for title, link in videos.items()]

    links_range = 'List!A:B'

    gs.write_data(links_range, data)

    additional_range = 'List!C:D'

    data = [
        ['Самоучитель', 'https://pythonworld.ru/samouchitel-python'],
        ['Онлайн компилятор', 'https://www.onlinegdb.com/online_python_compiler']
    ]
    gs.write_data(additional_range, data)

    info = gs.read_data('List!C:D')

    print(info)

    for i, c in info:
        print(i, c)


if __name__ == '__main__':
    main()
