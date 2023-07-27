# task: convert between midi to vector embedding
import pretty_midi
import numpy as np

# loading MIDI file and creating piano roll with note velocities
def midi_to_piano_roll(midi_path, fs=100, note_range=(21, 108), velocity_range=(0, 127), frame_size=100, hop_size=50):
    midi_data = pretty_midi.PrettyMIDI(midi_path)

    # Calculating total time steps based on given frame rate (fs)
    total_time_steps = int(np.ceil(midi_data.get_end_time() * fs))
    piano_roll = np.zeros((note_range[1] - note_range[0] + 1, total_time_steps))

    for instrument in midi_data.instruments:
        for note in instrument.notes:
            start_step = int(np.floor(note.start * fs))
            end_step = int(np.ceil(note.end * fs))
            pitch = int(note.pitch)
            velocity = int(note.velocity)
            velocity_normalized = (velocity - velocity_range[0]) / (velocity_range[1] - velocity_range[0])
            piano_roll[pitch - note_range[0], start_step:end_step] = velocity_normalized

    # Performing segmentation
    frame_size_steps = int(frame_size * fs)
    hop_size_steps = int(hop_size * fs)
    num_frames = int(np.ceil((total_time_steps - frame_size_steps) / hop_size_steps) + 1)
    piano_roll_segments = np.zeros((num_frames, piano_roll.shape[0], frame_size_steps))

    for i in range(num_frames):
        start_step = i * hop_size_steps
        end_step = start_step + frame_size_steps
        piano_roll_segments[i] = piano_roll[:, start_step:end_step]

    return piano_roll_segments

# creating vector embeddings using Autoencoder, simple mean reduction as embedding
def create_embeddings_with_autoencoder(piano_roll_segments):
    embeddings = np.mean(piano_roll_segments, axis=(1, 2))
    return embeddings

# Ex
midi_path = "Users/mindyslee/Downloadsto/midi/file.mid" 
piano_roll_segments = midi_to_piano_roll(midi_path)
embeddings = create_embeddings_with_autoencoder(piano_roll_segments)

# piano roll segments w note velocities btwn 0 and 1
# vector embeddings for further processing or analysis
print("Piano roll segments shape:", piano_roll_segments.shape)
print("Embeddings shape:", embeddings.shape)
