import os
import json
import pickle
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]
creds = None
if os.path.exists("token.pickle"):
    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        # NOTE: make sure that the path to client_secrets json file is correct in the next line
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret_readonly.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    with open("token.pickle", "wb") as token_file:
        pickle.dump(creds, token_file)

youtube = build("youtube", "v3", credentials=creds)

channels_response = youtube.channels().list(
    part="snippet,statistics,brandingSettings,contentOwnerDetails",
    id='UC0yXUUIaPVAqZLgRjvtMftw'
).execute()

# videos_response = youtube.search().list(
#     part='snippet,statistics',
#     channelId=channels_response["items"][0]["id"],
#     maxResults=50,
#     type='video'
# ).execute()

# save video response to a json file
# with open("video_response.json", "w") as json_file:
#     json.dump(videos_response, json_file, indent=4)

# save channel response to a json file
with open("channel_response.json", "w") as json_file:
    json.dump(channels_response, json_file, indent=4)

for channel in channels_response["items"]:
    print("Channel Title:", channel["snippet"]["title"])
    print("Channel ID:", channel["id"])
    print("Channel Description:", channel["snippet"]["description"])
    print("Subscriber Count:", channel["statistics"]["subscriberCount"])
    print("View Count:", channel["statistics"]["viewCount"])
    print("Video Count:", channel["statistics"]["videoCount"])
