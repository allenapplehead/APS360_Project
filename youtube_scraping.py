import yt_dlp as youtube_dl
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch
import csv
import re



# Create a YouTubeDL object

# Set the URL of the YouTube channel's main page

# Set the number of videos to retrieve
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

    csv_file_path = 'songs.csv'

    existing_lines = []
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        existing_lines = list(reader)

    new_lines = []
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
        ydl_opts = {
            'extract_flat': 'in_playlist',
            'skip_download': True,
            'youtube_include_dash_manifest': False,
            'extractor_args': {
                'youtube_search': {
                    'limit': num_results,
                }
            },
            'default-search': "ytsearch"
        }
        y_dl = YoutubeDL(ydl_opts)
        search_url = f"ytsearch:{search_query}"
        search_results = y_dl.extract_info(search_url, download=False)

        results = YoutubeSearch(search_query, max_results=num_results).to_dict()
        for result in results:
            print(f"Title: {video['title']}")
            print(f"Video ID: {video['id']}")
            print(f"URL: https://www.youtube.com/watch?v={video['id']}")
            print()
        #print(search_results['entries'])
        #search_results = search_results['entries'][:num_results]
        #print(len(search_results))
        url = video['webpage_url'].replace('https://www.youtube.com/watch?v=', '')
        for result in search_results:
            print(result['title'])
            if "Piano" not in result['title']:
                continue
            result_url = result['url']
            result_url = result_url.replace('https://www.youtube.com/watch?v=', '')
            new_lines.append([title, result['title'], url, result_url])

    updated_lines = existing_lines + new_lines

    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_lines)


csv_file = 'youtube_channels.csv'
with open(csv_file, 'r') as file:
    reader = csv.reader(file)
    rows = list(reader)

rows = rows[1:]
print(rows)

for row in rows:
    url = row[1]
    get_videos(url)