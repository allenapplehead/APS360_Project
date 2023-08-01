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


    piano_roll = np.transpose(piano_roll)
    piano_roll =  torch.tensor(piano_roll, dtype=torch.float32)

    return piano_roll



def postprocess(output, cover):
    # Gather range values
    min_note_threshold = 0.0001

    cover_zero_mask = cover == 0
    cover[cover_zero_mask] = 1

    max_velocity_cover = torch.max(cover).item() * 127
    cover_zero_mask = cover == 0
    cover[cover_zero_mask] = 1
    min_velocity_cover = torch.min(cover).item() * 127
    cover[cover_zero_mask] = 0

    max_value_output = torch.max(output).item()
    min_value_output = min_note_threshold

    # Rescale output range to song velocity range
    scaling = (max_velocity_cover - min_velocity_cover) / (max_value_output - min_value_output)

    # Begin output shift
    # output -= min_value_output
    output = output.clone() - min_value_output # create copy to avoid inplace modification
    
    # Cut values below threshold
    output[output < 0] = 0

    # Finish output scaling
    output *= scaling
    output[output != 0] += min_velocity_cover
    output /= 127
    
    return output