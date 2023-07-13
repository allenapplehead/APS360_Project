from __future__ import unicode_literals
import yt_dlp as youtube_dl
import librosa
import csv
import json

output_dir = 'dataset/'
video_id = 0

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }], 
    'outtmpl': f'{output_dir}/%(title)s.%(ext)s'
}


def get_songs(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    songs = data["songs"]
    return songs
songs = get_songs('songs.json')

for song in songs:
    song_filename = song["filename"]
    song_id = song["id"]
    covers = song["piano covers"]
    num_covers = len(covers["id"])
    for i in range(num_covers):
        cover_filename = covers["filename"][i]
        cover_id = covers["id"][i]
        # Extracting audio from pop music video
        pop_music = 'https://www.youtube.com/watch?v='+ song_id
        print(pop_music)
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([pop_music])  
        # Extracting audio from piano cover video
        piano_cover = 'https://www.youtube.com/watch?v=' + cover_id
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([piano_cover])

