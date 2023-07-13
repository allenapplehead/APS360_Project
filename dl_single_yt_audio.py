from __future__ import unicode_literals
import yt_dlp as youtube_dl

video_url = "https://www.youtube.com/watch?v=NgEaOJ7lRWY"

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([video_url])