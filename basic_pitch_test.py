import tensorflow as tf

from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

basic_pitch_model = tf.saved_model.load(str(ICASSP_2022_MODEL_PATH))
model_output, midi_data, note_events = predict("test_data/original.mp3", basic_pitch_model)

print("hello", note_events)