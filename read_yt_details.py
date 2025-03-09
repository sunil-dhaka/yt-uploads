import os
import json
import pickle
from typing import Any, Dict, List

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES: List[str] = ["https://www.googleapis.com/auth/youtube.readonly"]


class YouTubeAuthenticator:
    """
    Handles authentication for the YouTube API using OAuth credentials.

    Parameters
    ----------
    token_file : str
        Path to the token file to store user credentials.
    client_secrets_file : str
        Path to the client secrets JSON file.
    scopes : list of str
        List of scopes for the authentication.
    """

    def __init__(
        self,
        token_file: str = "token.pickle",
        client_secrets_file: str = "client_secret_readonly.json",
        scopes: List[str] = SCOPES,
    ) -> None:
        self.token_file = token_file
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes

    def authenticate(self) -> Any:
        """
        Authenticates and returns the user credentials.

        Returns
        -------
        Any
            User credentials after authentication.
        """
        creds = None
        if os.path.exists(self.token_file):
            with open(self.token_file, "rb") as token_file:
                creds = pickle.load(token_file)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # NOTE: make sure that the path to client_secrets.json file is correct.
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "wb") as token_file:
                pickle.dump(creds, token_file)
        return creds


class YouTubeService:
    """
    Provides methods to interact with the YouTube API.

    Parameters
    ----------
    credentials : Any
        Authenticated user credentials.
    """

    def __init__(self, credentials: Any) -> None:
        self.youtube = build("youtube", "v3", credentials=credentials)

    def get_channel_details(self, channel_id: str) -> Dict:
        """
        Retrieves channel details from YouTube.

        Parameters
        ----------
        channel_id : str
            The YouTube channel ID.

        Returns
        -------
        dict
            A dictionary with channel details and statistics.
        """
        response = self.youtube.channels().list(
            part="snippet,statistics,brandingSettings,contentOwnerDetails",
            id=channel_id
        ).execute()
        return response

    def save_channel_details(self, channel_id: str, output_file: str) -> None:
        """
        Retrieves channel details and saves the response to a JSON file.

        Parameters
        ----------
        channel_id : str
            The YouTube channel ID.
        output_file : str
            Path to the JSON file where details will be saved.
        """
        details = self.get_channel_details(channel_id)
        with open(output_file, "w") as json_file:
            json.dump(details, json_file, indent=4)

    def print_channel_details(self, channel_details: Dict) -> None:
        """
        Prints selected channel details to the console.

        Parameters
        ----------
        channel_details : dict
            A dictionary containing channel details.
        """
        for channel in channel_details.get("items", []):
            print("Channel Title:", channel["snippet"]["title"])
            print("Channel ID:", channel["id"])
            print("Channel Description:", channel["snippet"]["description"])
            print("Subscriber Count:", channel["statistics"]["subscriberCount"])
            print("View Count:", channel["statistics"]["viewCount"])
            print("Video Count:", channel["statistics"]["videoCount"])


def main() -> None:
    """
    Main function to authenticate, retrieve, and display YouTube channel details.
    """
    # Authenticate and build YouTube service
    authenticator = YouTubeAuthenticator()
    creds = authenticator.authenticate()
    yt_service = YouTubeService(credentials=creds)

    # Get channel details, save them and print to console
    channel_id = "UC0yXUUIaPVAqZLgRjvtMftw"
    channel_details = yt_service.get_channel_details(channel_id)
    yt_service.save_channel_details(channel_id, "channel_response.json")
    yt_service.print_channel_details(channel_details)


if __name__ == "__main__":
    main()