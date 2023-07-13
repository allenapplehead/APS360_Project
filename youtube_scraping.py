import yt_dlp as youtube_dl
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
            #Getting the Piano Cover
        search_query = title + ' Piano Cover'
        search_url = f"ytsearch:{search_query}"
        search_results = ydl.extract_info(search_url, download=False)
        url = video['webpage_url'].replace('https://www.youtube.com/watch?v=', '')
        result_url = search_results['entries'][0]['webpage_url']
        result_url = result_url.replace('https://www.youtube.com/watch?v=', '')
        new_lines.append([title, url, result_url])

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