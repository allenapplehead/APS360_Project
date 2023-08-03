#import pretty_midi # removed bc theres conflict in set_tempo bc both libraries have it 
import numpy as np
from mido import MidiFile, MidiTrack, Message, MetaMessage

def piano_roll_to_midi(piano_roll, tempo=500000):  #120bpm we can adjust tempo if we want

    # Create MIDI file
    mid = MidiFile(ticks_per_beat=480) 
    track = MidiTrack()
    mid.tracks.append(track)

    # tempo as MetaMessage
    tempo_value = int(60 * 10**6 / tempo)  #seconds to microseconds
    meta_msg = MetaMessage('set_tempo', tempo=tempo_value)
    track.append(meta_msg)
    
    tick_duration = mid.ticks_per_beat / 4 

    for time_step, notes in enumerate(piano_roll):
        for note in notes:
            if note is not None:
                note_number, velocity = note
                note_on = Message('note_on', note=note_number, velocity=velocity, time=0)
                note_off = Message('note_off', note=note_number, velocity=0, time=tick_duration)
                track.append(note_on)
                track.append(note_off)

    return mid

# midi_file_output = 'midifilepath.mid'  #change
# midi_file = piano_roll_to_midi(piano_roll) #replace
# midi_file.save(midi_file_output)
