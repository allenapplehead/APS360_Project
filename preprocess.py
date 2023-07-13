import tensorflow as tf
import librosa
import os

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

import audio_alignment_v2

class SongPianoPair():
    def __init__(self, raw_song_audio, raw_piano_audio_path, output_song_midi_path, output_piano_midi_path, temp_song_audio_path="temp.wav"):
        self.raw_song_audio = raw_song_audio
        self.raw_piano_audio_path = raw_piano_audio_path
        self.raw_piano_midi = None

        self.temp_song_audio_path = temp_song_audio_path
        self.song_midi_path = output_song_midi_path
        self.piano_midi_path = output_piano_midi_path
        self.song_midi = None
        self.piano_midi = None

    def preprocess(self, basic_pitch_model):
        print("1")
        _, self.raw_piano_midi, _ = predict(self.raw_piano_audio_path, basic_pitch_model)
        print("2")
        audio_alignment_v2.align_song_piano(self, False)
        print("3")
        _, self.song_midi, _ = predict(self.temp_song_audio_path, basic_pitch_model)
        self.song_midi.write(self.song_midi_path)
        print("4")
        os.remove(self.temp_song_audio_path)

basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))

print("0")
song_audio, _ = librosa.load("test_data/source_0001.wav", sr=audio_alignment_v2.Fs)
pair = SongPianoPair(song_audio, "test_data/target_0001-1.wav", "song_midi.midi", "piano_midi.midi")
pair.preprocess(basic_pitch_model)








if __name__ == "__main__":
    basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))

