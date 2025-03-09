#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate conda environment
conda activate yt_v3

# enable autocomplete
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# set the input folder path
read -e -p "folder path that needs to be uplaoded " input_folder

# python file path that needs to be executed
read -e -p "script path (relative to this script): " script_path_relative
script_path="$script_path_relative"

# check if the script exists
if [ ! -f "$script_path" ]; then
    echo "Error: Script file not found at $script_path"
    echo "Default path will be used: upload.py"
    script_path="upload.py"
fi

# loop through all video files in the input folder
for video_file in "$input_folder"/*.mp4; do
    # get the video file name without the extension
    video_name=$(basename "$video_file" .mp4)

    # get the folder name containing the video file
    folder_name=$(basename "$(dirname "$video_file")")

    # set the video title to the file name and the video description to the folder name
    title="$video_name"
    description="$folder_name"

    # upload the video using the Python script
    python "$script_path" --file "$video_file" --title "$title" --description "$description" --privacyStatus "private"

    # remove the video file after it has been uploaded
    # rm "$video_file"
done

# Deactivate conda environment
conda deactivate
