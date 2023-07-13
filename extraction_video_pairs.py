from __future__ import unicode_literals
import yt_dlp as youtube_dl
import librosa
import csv

output_dir = 'test_data/'
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }], 
    'outtmpl': f'{output_dir}/%(title)s.%(ext)s'
}


def get_songs(csv_file):
    songs = []
    first_row = True
    with open(csv_file, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if first_row:
                first_row = False
                continue
            songs.append(row)
    return songs
video_pairs = get_songs('songs.csv')

for pair in video_pairs:
    # Extracting audio from pop music video
    pop_music = 'https://www.youtube.com/watch?v='+ pair[1]
    print(pop_music)
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([pop_music])  
    # Extracting audio from piano cover video
    piano_cover = 'https://www.youtube.com/watch?v=' + pair[2]
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([piano_cover])

