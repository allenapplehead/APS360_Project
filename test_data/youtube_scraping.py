import yt_dlp as youtube_dl
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import csv
import re
import sys
import json

# Set the encoding
sys.stdout.reconfigure(encoding='utf-8')

def has_non_encodable_characters(text, encoding='utf-8'):
    try:
        text.encode(encoding)
        return False
    except UnicodeEncodeError:
        return True

def get_videos(channel_url):
    ydl = youtube_dl.YoutubeDL()
    num_videos = 15

    # Set the options for extracting the videos
    options = {
        'extract_flat': True,   # Extract only videos, not playlists or other content
    }

    # Extract information about all videos in the channel's playlist
    all_videos = ydl.extract_info(channel_url, download=False, extra_info=options)

    # Sort the videos based on the popularity metric (e.g., views)
    popular_videos = sorted(all_videos['entries'], key=lambda x: x['view_count'], reverse=True)

    # Retrieve the top N popular videos
    top_videos = popular_videos[:num_videos]

    # Print the information of the top videos


    for video in top_videos:
        title = video['title']
        if 'Lyric' in title:
            continue
        if 'Live' in title:
            continue
        
        # Getting the Piano Cover
        num_results = 5
        search_query = title + ' Piano Cover'

        # Configure the options for the youtube_search plugin

        results = YoutubeSearch(search_query, max_results=num_results).to_dict()

        url = video['webpage_url'].replace('https://www.youtube.com/watch?v=', '')
        
        data = {"filename" : (title + '.wav'), 
                "piano covers": {"id": [], 
                                 "filename" : []}, 
                "id": url}

        for result in results:
            print(result['title'])
            if "Piano" not in result['title'] and "piano" not in result['title']:
                continue
            if has_non_encodable_characters(title):
                continue
            if has_non_encodable_characters(result['title']):
                continue
            if ',' in title or ',' in result['title']:
                continue

            data["piano covers"]["id"].append(result['id'])
            data["piano covers"]["filename"].append(result['title'] + '.wav')
        
        file_path = 'songs.json'
        with open(file_path, "r") as json_file:
            existing_data = json.load(json_file)
        
        existing_array = existing_data["songs"]
        existing_array.append(data)

        print(existing_data)
        
        with open(file_path, "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
        

csv_file = 'youtube_channels.csv'
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    rows = list(reader)

rows = rows[1:]
print(rows)

for row in rows:
    url = row[1]
    get_videos(url)