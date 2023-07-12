import youtube_dl
import librosa


video_pairs = [
    {
        'pop_music': 'https://youtu.be/NgEaOJ7lRWY',
        'piano_cover': 'https://youtu.be/GDzy4AXetlI' # super shy
    },
    {
        'pop_music': 'https://youtu.be/AIYpdjQVidc',
        'piano_cover': 'https://youtu.be/gKooKVUwpwo' # rolling in the deep
    },
    {
        'pop_music': 'https://youtu.be/Fqey8LxQxFU',
        'piano_cover': 'https://youtu.be/Qq_Ds5nJUB4' # vampire
    },
    {
        'pop_music': 'https://youtu.be/lwAHfOhOONw',
        'piano_cover': 'https://youtu.be/RNLCqUfbPkE' # take two
    },
    {
        'pop_music': 'https://youtu.be/5Ejp7yFZxPM',
        'piano_cover': 'https://youtu.be/eSjVVCmAJTE' # cupid
    },
    {
        'pop_music': 'https://youtu.be/lzomiJ3mZXY',
        'piano_cover': 'https://youtu.be/VXsYKNWKS20' # eyes closed
    },
    {
        'pop_music': 'https://youtu.be/kSfx0OvkxJM',
        'piano_cover': 'https://youtu.be/PF0WdWwUMdI' # diamonds
    },
    {
        'pop_music': 'https://youtu.be/J_BId2d5zB4',
        'piano_cover': 'https://youtu.be/8qMjwA_Q-98' # I'm not the only one
    },
    {
        'pop_music': 'https://youtu.be/BsMO72SBAfo',
        'piano_cover': 'https://youtu.be/2cMGsLZZxec' # kill bill
    },
    {
        'pop_music': 'https://youtu.be/sGp-tnr0u5M',
        'piano_cover': 'https://youtu.be/sbbSlarFkvY' # baby
    },
    {
        'pop_music': 'https://youtu.be/XqN2qFvY64U',
        'piano_cover': 'https://youtu.be/pzlqsVIm7yA' # anti-hero
    },
    {
        'pop_music': 'https://youtu.be/VJruS2ULZoY',
        'piano_cover': 'https://youtu.be/S8TvXhLtLa0' # golden hour
    },
    {
        'pop_music': 'https://youtu.be/VJruS2ULZoY',
        'piano_cover': 'https://youtu.be/S8TvXhLtLa0' # golden hour
    },
    {
        'pop_music': 'https://youtu.be/oUxfHBktaLE',
        'piano_cover': 'https://youtu.be/MzapYDVqLHo' # hello
    },
    { 
        'pop_music': 'https://youtu.be/fKRmN7Ro1B0',
        'piano_cover': 'https://youtu.be/IhbLmOtAAug' # tally
    },
    {
        'pop_music': 'https://youtu.be/hHKRrRdH_7Q',
        'piano_cover': 'https://youtu.be/W4auGVefufE' # call me maybe 
    },
    {
        'pop_music': 'https://youtu.be/UFQGgJmjQYk',
        'piano_cover': 'https://youtu.be/4idiUM4SpUA' # grenade
    },
    {
        'pop_music': 'https://youtu.be/nAQ_1lTDvPQ',
        'piano_cover': 'https://youtu.be/oe7A7HjZhHU' # blank space
    },
    {
        'pop_music': 'https://youtu.be/s60sh-vjzno',
        'piano_cover': 'https://youtu.be/YCjsVNY2pjE' # that's hilarious
    },
    {
        'pop_music': 'https://youtu.be/fuP4Lkt1vAo',
        'piano_cover': 'https://youtu.be/FbDFUsSwIz4' # payphone
    },
    {
        'pop_music': 'https://youtu.be/JBe0yHNEURo',
        'piano_cover': 'https://youtu.be/rmKcIx-CxTU' # abcdefu
    },
    
    
    # Add more pairs of URLs as needed
]

ydl_opts = {
    'format': 'bestaudio/best',  
    'outtmpl': '%(title)s.%(ext)s',  
    'noplaylist': True,  # trying to resolve issue w youtube-dl
}


for pair in video_pairs:
    # Extracting audio from pop music video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([pair['pop_music']])
    pop_music_file = ydl.prepare_filename(ydl.extract_info(pair['pop_music'], download=False))

    y, sr = librosa.load(pop_music_file, sr=None)
    audio_file = 'pop_music_audio.wav'
    librosa.output.write_wav(audio_file, y, sr)

    # Extracting audio from piano cover video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([pair['piano_cover']])
    piano_cover_file = ydl.prepare_filename(ydl.extract_info(pair['piano_cover'], download=False))

    y, sr = librosa.load(piano_cover_file, sr=None)
    audio_file = 'piano_cover_audio.wav'
    librosa.output.write_wav(audio_file, y, sr)