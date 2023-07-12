import glob
import os
import music21

from basic_pitch.inference import predict_and_save
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

model_output, midi_data, note_events = predict("test_data/original.mp3")
predict_and_save( ["test_data/original.mp3"], "midi_data", True, False, False, True)
#converting everything into the key of C major or A minor

# major conversions
majors = dict([("A-", 4),("A", 3),("A#", 2),("B-", 2),("B", 1),("C", 0),("C#", -1),("D-", -1), ("D", -2),("E-", -3),("E", -4),("F", -5),("G-", 6),("G", 5)])
minors = dict([("A-", 1),("G#", 1),("A", 0),("B-", -1),("B", -2),("C", -3),("D-", -4),("C#", -4),("D", -5),("E-", 6),("E", 5),("F", 4),("G-", 3),("G", 2)])


#os.chdir("./")

# Transposes Keys
def transpose_key(filename):
    for file in glob.glob(filename):
        score = music21.converter.parse(file)
        key = score.analyze('key')
    #    print key.tonic.name, key.mode
        if key.mode == "major":
            halfSteps = majors[key.tonic.name]
            
        elif key.mode == "minor":
            halfSteps = minors[key.tonic.name]
        
        newscore = score.transpose(halfSteps)
        key = newscore.analyze('key')
        print (key.tonic.name, key.mode)
        newFileName = "C_" + file
        #newscore.write('midi',newFileName)
    return newscore


#Shift octaves

def getMusicProperties(x):
    s = ''
    t=''
    s = str(x.pitch) + ", " + str(x.duration.type) + ", " + str(x.duration.quarterLength)
    s += ", "
    if x.tie != None:
        t = x.tie.type
    s += t + str(x.pitch.ps) + ", " + str(x.octave) 
    return s

def get_average_octave(score):

    partStream = score.parts.stream()
    octave_count = 0
    num_notes = 0
    for n in partStream.flat.notes:
        if (n.isNote):
            s = n.octave
            octave_count += int(s)
            num_notes += 1
        if (n.isChord):
            for x in n._notes:
                s = x.octave
                octave_count += int(s)
                num_notes += 1
    
    return octave_count//num_notes

def write_file(file, score):
    newFileName = "C_" + file
    score.write('midi',newFileName)

def main():
    source = "basic_pitch_transcription.mid"
    target = "basic_pitch_transcription (1).mid"

    source_score = transpose_key(source)
    target_score = transpose_key(target)

    source_octave = get_average_octave(source_score)
    target_octave = get_average_octave(target_score)

    half_steps = (source_octave - target_octave)*12

    new_target_score = target_score.transpose(half_steps)

main()
        
    
