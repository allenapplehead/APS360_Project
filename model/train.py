
import torch
import torch.nn as nn
import math
import numpy as np
import torch.nn.functional as F

from model import Net

#Turn midi into piano roll

import pretty_midi
import numpy as np

midi_folder = 'data/clean_data/0_0_cover.midi'

def midi_to_piano_roll(midi_file_path, time_resolution=100):
    # Load MIDI file using pretty_midi
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)

    # Get the total length of the MIDI data in seconds
    total_time = midi_data.get_end_time()

    # Calculate the number of time steps based on the specified time resolution
    num_time_steps = int(np.ceil(total_time * time_resolution))

    # Initialize the piano roll matrix with all zeros
    piano_roll = np.zeros((128, num_time_steps), dtype=int)

    # Iterate through the notes in the MIDI data and fill the piano roll
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            # Get the start and end time of the note in seconds
            start_time = note.start
            end_time = note.end

            # Convert start and end time to time steps
            start_time_step = int(np.floor(start_time * time_resolution))
            end_time_step = int(np.ceil(end_time * time_resolution))

            # Set the corresponding elements in the piano roll to 1 for the duration of the note
            pitch = int(note.pitch)
            piano_roll[pitch, start_time_step:end_time_step] = note.velocity/127

    return piano_roll

import pretty_midi

def get_note_velocity(midi_file_path):
    # Load MIDI file using pretty_midi
    midi_data = pretty_midi.PrettyMIDI(midi_file_path)

    # Dictionary to store note velocities for each instrument
    note_velocities = {}

    # Iterate through the instruments in the MIDI data
    for instrument in midi_data.instruments:
        # List to store note velocities for the current instrument
        velocities = []
        # Iterate through the notes in the instrument
        for note in instrument.notes:
            # Append the velocity of the current note to the list
            velocities.append(note.velocity)
        # Store the list of velocities for the current instrument in the dictionary
        note_velocities[instrument.program] = velocities

    return note_velocities

# Example usage:
midi_file_path = 'data/clean_data/0_0_cover.midi'
note_velocities = get_note_velocity(midi_file_path)

# The 'note_velocities' dictionary will contain note velocities for each instrument,
# where the instrument program number is the key and the list of velocities is the value.


# Example usage:
midi_file_path = 'data/clean_data/1_1_cover.midi'
piano_roll = midi_to_piano_roll(midi_file_path)
print(piano_roll.shape)  # (128, num_time_steps)

piano_roll = np.transpose(piano_roll)
piano_roll_tensor =  torch.tensor(piano_roll, dtype=torch.float32).unsqueeze(0)

print(piano_roll_tensor.shape)

for line in piano_roll:
    if np.all(line == 0):
        continue
    else:
        print(line)



model = Net(width = 10)
piano_roll_tensor = piano_roll_tensor
out = model(piano_roll_tensor)

out = F.softmax(out, dim = 1)

print(out)
