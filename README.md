# YouTube Video Uploader

A tool for automating YouTube video uploads using the YouTube Data API v3.

## Prerequisites

To make things work you have to go through some oAuth stuff, and get credentials.
Here's something to help with that:
- [automate-video-uploads](https://sunil-dhaka.github.io/automation/automate-video-uploads.html)

## Getting Started

### Setting up with Conda Environment

1. Clone this repository to your local machine
2. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution) if not already installed
3. Create and activate the environment using the provided `environment.yml` file:

```bash
conda env create -f environment.yml
conda activate yt_v3
```

The environment will install Python 3.12 and all required dependencies for working with the YouTube API.

### Alternative: Using pip

If you prefer not to use Conda, you can set up a virtual environment with pip:

```bash
python -m venv yt_env
source yt_env/bin/activate  # On Windows, use: yt_env\Scripts\activate
pip install -r requirements.txt
```

## Project Structure

```
.
├── .gitignore                     # Git ignore file
├── client_secret.json             # OAuth 2.0 credentials from Google API Console
├── environment.yml                # Conda environment specification
├── LICENSE                        # Project license
├── read_yt_details.py             # Script to read video details from YouTube
├── README.md                      # Project documentation
├── requirements.txt               # Python dependencies for pip
├── upload_folders_to_youtube.sh   # Shell script to upload multiple folders
├── upload_single_video.sh         # Shell script to upload a single video
├── upload.py                      # Main script for YouTube uploads
├── test_vids/                     # Example videos for testing
│   └── Herland.mp4
└── yt_v3_api/                     # Virtual environment directory
```

## How upload.py Works

The `upload.py` script is the core component of this project and handles the YouTube upload process:

1. **Authentication**: Uses OAuth 2.0 flow to authenticate with the YouTube API
   - Reads credentials from `client_secret.json`
   - Stores authentication tokens in `*-oauth2.json` files for later use

2. **Video Upload Process**:
   - Parses command-line arguments (title, description, privacy status, etc.)
   - Prepares video metadata and initiates the upload
   - Implements exponential backoff for retrying failed uploads

3. **Error Handling**:
   - Implements retry logic for transient errors
   - Provides detailed logging of upload progress and errors

Usage example:
```bash
python upload.py --file="test_vids/Herland.mp4" --title="My Video" --description="A test upload" --keywords="test,upload" --privacyStatus="unlisted"
```

## Common Issues and Troubleshooting

### Handling Errors

- **Quota errors**: Can't do anything except try again the next day when quota is reset
- **Credential issues**: Need to populate client_secret.json in specific format, otherwise it will throw errors
- **Authorization**: When authorization is done, it will create a file called `script_name-oAuth.json`, which will be used for future authorization. If you want to change the account, you need to delete this file and re-run the script, then reauthorize the account you want to use.
- **Different accounts**: Don't forget to change the client_secret.json file for different accounts, otherwise it will use the same account as before and give quota errors

### Warnings

- To make this stuff work is not easy because of certain factors. Main one is Google keeps changing things and Google is very strict about multiple oAuth. Even after so much work, I could not make it fully automated. I have to go to browser to click on one button. One benefit these scripts have is that you can batch process your folders, so that manual oAuth is a one-time deal.
- YouTube API v3 has quota restrictions, as mentioned in errors.
- So if you are stuck, then you are on your own.