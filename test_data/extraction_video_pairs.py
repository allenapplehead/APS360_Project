from __future__ import unicode_literals
import yt_dlp as youtube_dl
import librosa
import csv
import json

output_dir = 'dataset/'
video_id = 0



def get_songs(file_path):
    with open(file_path, "r") as json_file:
        data = json.load(json_file)
    songs = data["songs"]
    return songs
songs = get_songs('songs.json')

num_song = 0

for song in songs:

    ydl_opts_song = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192',
    }], 
    'outtmpl': f'{output_dir}/{num_song}_song.%(ext)s'
    }
    song_filename = song["filename"]
    song_id = song["id"]

    # Extracting audio from pop music video
    pop_music = 'https://www.youtube.com/watch?v='+ song_id
    print(pop_music)
    with youtube_dl.YoutubeDL(ydl_opts_song) as ydl:
        ydl.download([pop_music])  
    
    covers = song["piano covers"]
    num_covers = len(covers["id"])
    for i in range(num_covers):
        ydl_opts_cover = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }], 
            'outtmpl': f'{output_dir}/{num_song}_{i}_cover.%(ext)s'
        }

        cover_filename = covers["filename"][i]
        cover_id = covers["id"][i]

        # Extracting audio from piano cover video
        piano_cover = 'https://www.youtube.com/watch?v=' + cover_id
        with youtube_dl.YoutubeDL(ydl_opts_cover) as ydl:
            ydl.download([piano_cover])
    num_song += 1

