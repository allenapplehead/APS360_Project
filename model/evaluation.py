## Quantitative evaluation metrics for the model

import torch
import pretty_midi
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score

def get_accuracy(net, train_loader, val_loader, test_loader, which="train", use_cuda=False):

    """ 
        Computes the accuracy of the model on the train, validation and test sets 
        
        Args:
            net: the model
            train_loader: the train set data loader
            val_loader: the validation set data loader
            test_loader: the test set data loader
            which: which set to compute the accuracy for ("train", "val", "test")
            use_cuda: whether to use cuda or not (False, True)
            
        Returns:
            The accuracy of the model on the specified set
    """

    # Define the data loader set
    if which == "train":
        data_loader = train_loader
    elif which == "val":
        data_loader = val_loader
    elif which == "test":
        data_loader = test_loader
    else:
        raise NotImplementedError
    
    correct = 0
    total = 0
    for imgs, labels in data_loader:

        # enable GPU if available
        if use_cuda and torch.cuda.is_available():
          imgs = imgs.cuda()
          labels = labels.cuda()

        # network prediction
        output = net(imgs)

        #select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]
    return correct / total
    



def midi_note_pitch_accuracy(file1, file2, start_time1=None, end_time1=None, start_time2=None, end_time2=None):
    # Load the MIDI files
    midi1 = pretty_midi.PrettyMIDI(file1)
    midi2 = pretty_midi.PrettyMIDI(file2)

    # Extract the piano roll of each MIDI file
    piano_roll1 = midi1.get_piano_roll(fs=100)
    piano_roll2 = midi2.get_piano_roll(fs=100)

    # If start and end times are specified, convert them to frame indices and slice the piano rolls
    if start_time1 is not None and end_time1 is not None:
        start_frame1 = int(start_time1 * 100)
        end_frame1 = int(end_time1 * 100)
        piano_roll1 = piano_roll1[:, start_frame1:end_frame1]

    if start_time2 is not None and end_time2 is not None:
        start_frame2 = int(start_time2 * 100)
        end_frame2 = int(end_time2 * 100)
        piano_roll2 = piano_roll2[:, start_frame2:end_frame2]

    # If the piano rolls have different numbers of columns, truncate the longer one to match the shorter one
    min_length = min(piano_roll1.shape[1], piano_roll2.shape[1])
    piano_roll1 = piano_roll1[:, :min_length]
    piano_roll2 = piano_roll2[:, :min_length]

    # Get the note pitch at each time step by finding the index of the maximum value in each column
    note_sequence1 = np.argmax(piano_roll1, axis=0)
    note_sequence2 = np.argmax(piano_roll2, axis=0)

    # Compute the note pitch accuracy by comparing the note sequences
    correct_notes = np.sum(note_sequence1 == note_sequence2)
    total_notes = len(note_sequence1)
    note_accuracy = correct_notes / total_notes

    return note_accuracy


# Note the issue with the below method is as long as any two notes are played at the same
# time its considered a match, but the notes played could be like completely wrong
def midi_note_accuracy_w_playability(file1, file2, start_time1=None, end_time1=None, start_time2=None, end_time2=None):
    # Load the MIDI files
    midi1 = pretty_midi.PrettyMIDI(file1)
    midi2 = pretty_midi.PrettyMIDI(file2)

    # Extract the piano roll of each MIDI file
    piano_roll1 = midi1.get_piano_roll(fs=100)
    piano_roll2 = midi2.get_piano_roll(fs=100)

    # Convert the piano rolls to binary (note on/off)
    binary_roll1 = np.where(piano_roll1 > 0, 1, 0)
    binary_roll2 = np.where(piano_roll2 > 0, 1, 0)

    # If start and end times are specified, convert them to frame indices and slice the binary rolls
    if start_time1 is not None and end_time1 is not None:
        start_frame1 = int(start_time1 * 100)
        end_frame1 = int(end_time1 * 100)
        binary_roll1 = binary_roll1[:, start_frame1:end_frame1]

    if start_time2 is not None and end_time2 is not None:
        start_frame2 = int(start_time2 * 100)
        end_frame2 = int(end_time2 * 100)
        binary_roll2 = binary_roll2[:, start_frame2:end_frame2]

    # If the binary rolls have different numbers of columns, truncate the longer one to match the shorter one
    min_length = min(binary_roll1.shape[1], binary_roll2.shape[1])
    binary_roll1 = binary_roll1[:, :min_length]
    binary_roll2 = binary_roll2[:, :min_length]

    # Compute precision, recall, and F1 score
    precision = precision_score(binary_roll1.flatten(), binary_roll2.flatten())
    recall = recall_score(binary_roll1.flatten(), binary_roll2.flatten())
    f1 = f1_score(binary_roll1.flatten(), binary_roll2.flatten())

    # Calculate the penalties
    polyphony_penalty = np.sum(np.sum(binary_roll2, axis=0) > 10) / binary_roll2.shape[1]
    note_density_penalty = np.sum(binary_roll2) / binary_roll2.shape[1] > 20  # threshold = 20 notes per time unit
    note_jumps_penalty = np.average(np.abs(np.diff(np.argmax(binary_roll2, axis=0)))) > 10  # threshold = 10 semi-tones

    # Apply the penalties to the F1 score
    f1 -= (polyphony_penalty + note_density_penalty + note_jumps_penalty)

    return precision, recall, f1