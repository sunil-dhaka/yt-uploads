#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment
conda activate yt_v3

# enable autocomplete
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# prompt the user for the video file path
read -e -p "Enter the path to the video file: " file_path

# prompt the user for the video title
read -e -p "Enter the video title (leave blank for no title): " title

# prompt the user for the video description
read -e -p "Enter the video description (leave blank for no description): " description

# prompt the user for the video keywords
read -e -p "Enter the video keywords (leave blank for no keywords): " keywords

# prompt the user for the video privacy status
echo "Enter the video privacy status:"
echo "1. Public"
echo "2. Unlisted"
echo "3. Private"
read -p "Enter your choice (default is Public): " privacy_choice

# set the privacy status based on the user's choice
if [ "$privacy_choice" = "2" ]; then
    privacy_status="unlisted"
elif [ "$privacy_choice" = "3" ]; then
    privacy_status="private"
else
    privacy_status="public"
fi

# Use the Python interpreter from the conda environment to run the upload.py script
python "upload.py" --file "$file_path" --title "$title" --description "$description" --keywords "$keywords" --privacyStatus "$privacy_status"

# Deactivate conda environment
conda deactivate