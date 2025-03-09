#!/usr/bin/python

import logging
import httplib2
import os
import random
import sys
import time

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# Get the current directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging
LOG_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), "logs", "upload.log")
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Explicitly tell the underlying HTTP transport library not to retry, since
# we are handling retry logic ourselves.
httplib2.RETRIES = 1

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, "client_secret.json")
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the API Console
https://console.cloud.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(CLIENT_SECRETS_FILE)

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


def get_authenticated_service(args):
    """
    Authenticate and return the YouTube service object.

    Parameters
    ----------
    args : argparse.Namespace
        Command line arguments.

    Returns
    -------
    googleapiclient.discovery.Resource
        Authenticated YouTube service object.
    """
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                                   scope=YOUTUBE_UPLOAD_SCOPE,
                                   message=MISSING_CLIENT_SECRETS_MESSAGE)

    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()

    if credentials is None or credentials.invalid:
        credentials = run_flow(flow, storage, args)

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                 http=credentials.authorize(httplib2.Http()))


def initialize_upload(youtube, options):
    """
    Initialize and start the video upload process.

    Parameters
    ----------
    youtube : googleapiclient.discovery.Resource
        Authenticated YouTube service object.
    options : argparse.Namespace
        Command line arguments.
    """
    tags = None
    if options.keywords:
        tags = options.keywords.split(",")

    body = dict(
        snippet=dict(
            title=options.title,
            description=options.description,
            tags=tags,
            categoryId=options.category
        ),
        status=dict(
            privacyStatus=options.privacyStatus
        )
    )

    insert_request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=MediaFileUpload(options.file, chunksize=-1, resumable=True)
    )

    resumable_upload(insert_request)


def resumable_upload(insert_request):
    """
    Implement an exponential backoff strategy to resume a failed upload.

    Parameters
    ----------
    insert_request : googleapiclient.http.HttpRequest
        The HTTP request for the video upload.
    """
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            logging.info("Uploading file...")
            status, response = insert_request.next_chunk()
            if response is not None:
                if 'id' in response:
                    logging.info("Video id '%s' was successfully uploaded." % response['id'])
                else:
                    logging.error("The upload failed with an unexpected response: %s" % response)
                    exit("The upload failed with an unexpected response: %s" % response)
        except HttpError as e:
            if e.resp.status in RETRIABLE_STATUS_CODES:
                error = "A retriable HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = "A retriable error occurred: %s" % e

        if error is not None:
            logging.warning(error)
            retry += 1
            if retry > MAX_RETRIES:
                logging.error("No longer attempting to retry.")
                exit("No longer attempting to retry.")

            max_sleep = 2 ** retry
            sleep_seconds = random.random() * max_sleep
            logging.info("Sleeping %f seconds and then retrying..." % sleep_seconds)
            time.sleep(sleep_seconds)


if __name__ == '__main__':
    argparser.add_argument("--file", required=True, help="Video file to upload")
    argparser.add_argument("--title", help="Video title", default="Test Title")
    argparser.add_argument("--description", help="Video description", default="Test Description")
    argparser.add_argument("--category", default="22",
                           help="Numeric video category. " +
                                "See https://developers.google.com/youtube/v3/docs/videoCategories/list")
    argparser.add_argument("--keywords", help="Video keywords, comma separated", default="")
    argparser.add_argument("--privacyStatus", choices=VALID_PRIVACY_STATUSES,
                           default=VALID_PRIVACY_STATUSES[0], help="Video privacy status.")
    args = argparser.parse_args()

    if not os.path.exists(args.file):
        logging.error("Please specify a valid file using the --file= parameter.")
        exit("Please specify a valid file using the --file= parameter.")

    youtube = get_authenticated_service(args)
    try:
        initialize_upload(youtube, args)
    except HttpError as e:
        logging.error("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
        print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
