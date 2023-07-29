#Turn midi into piano roll

import pretty_midi
import numpy as np
import torch

def midi_to_piano_roll(midi_file_path, time_resolution=100):
    # Load MIDI file using pretty_midi
    try:
        midi_data = pretty_midi.PrettyMIDI(midi_file_path)
    except:
        return None

    total_time = midi_data.get_end_time()

    num_time_steps = int(np.ceil(total_time * time_resolution))

    piano_roll = np.zeros((128, num_time_steps), dtype=np.float32)


    for instrument in midi_data.instruments:
        for note in instrument.notes:

            start_time = note.start
            end_time = note.end

            start_time_step = int(np.floor(start_time * time_resolution))
            end_time_step = int(np.ceil(end_time * time_resolution))

            pitch = int(note.pitch)
            piano_roll[pitch, start_time_step:end_time_step] = note.velocity/127


    sum= 0
    for i in range(len(piano_roll)):
        for j in range(len(piano_roll[i])):
            sum += piano_roll[i][j]

    piano_roll = np.transpose(piano_roll)
    piano_roll =  torch.tensor(piano_roll, dtype=torch.float32)

    return piano_roll

