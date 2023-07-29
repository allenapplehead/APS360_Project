
import torch
import torch.nn as nn
import math
import numpy as np
import torch.nn.functional as F

from model import Net

#Turn midi into piano roll

import pretty_midi
import numpy as np
from midi_to_piano_roll import midi_to_piano_roll

midi_folder = 'data/clean_data/0_0_cover.midi'

# Example usage:
midi_file_path = 'data/clean_data/0_0_cover.midi'


# Example usage:
midi_file_path = 'data/clean_data/1_1_song.midi'
piano_roll = midi_to_piano_roll(midi_file_path)
print(piano_roll.shape)  # (128, num_time_steps)

piano_roll_tensor =  torch.tensor(piano_roll, dtype=torch.float32).unsqueeze(0)

print(piano_roll_tensor.shape)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#model = Net(width = 10)
piano_roll_tensor = piano_roll_tensor

piano_roll_tensor_val = piano_roll_tensor[:,:,:10000]
print(piano_roll_tensor_val.shape)
print(piano_roll_tensor_val)
#out = model(piano_roll_tensor)


'''
def find_note(threshold, line):
    num = 0
    for note in line:
        if note > threshold:
            num += 1
    return num
num_notes = []
for line in out:
    num = find_note(0.001, line)
    if num > 0:
        num_notes.append(num)
    else:
        num_notes.append(0)

print(num_notes)
'''