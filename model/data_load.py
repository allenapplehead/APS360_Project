# Load from USB
import json
import os
import torch
import numpy as np
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
import torch.optim as optim

import pretty_midi
from model import Net
from midi_to_piano_roll import midi_to_piano_roll
from loss import blur_loss

IN_FOLDER = 'data/clean_data/'

file_path = "data/songs.json"
with open(file_path, "r") as json_file:
        songs_file = json.load(json_file)

def extend(data, max_length):
    new_data = []
    for i in range(len(data)):
        rows_needed = max_length - data[i][0].shape[0]
        zeros_to_add = torch.zeros((rows_needed, 128), dtype=data[i][0].dtype)
        new_song= torch.concatenate((data[i][0], zeros_to_add), axis=0)

        rows_needed = max_length - data[i][1].shape[0]
        zeros_to_add = torch.zeros((rows_needed, 128), dtype=data[i][1].dtype)
        new_cover= torch.concatenate((data[i][1], zeros_to_add), axis=0)
        
        new_data.append((new_song, new_cover))
    return new_data

def get_data():
    training_data = []
    validation_data = []
    testing_data = []

    count = 0
    max_length = 0
    for song in songs_file["songs"]:
        song_file = song["filename"]
        song_num = int(song_file.split("_")[0])
        for piano_file in song["piano covers"]["filename"]:
            
            name = os.path.splitext(piano_file)[0].split('_')[0] + "_" + os.path.splitext(piano_file)[0].split('_')[1]
            song_file_path = IN_FOLDER + name + "_song.midi"
            cover_file_path = IN_FOLDER + name + "_cover.midi"

            song_piano_roll = midi_to_piano_roll(song_file_path)
            cover_piano_roll = midi_to_piano_roll(cover_file_path)

            if song_piano_roll == None or cover_piano_roll == None:
                continue

            song_piano_roll_val = song_piano_roll[:song_piano_roll.shape[-1]//2, :]
            cover_piano_roll_val = cover_piano_roll[:cover_piano_roll.shape[-1]//2, :]
            
            song_length = song_piano_roll.shape[0]
            cover_length = cover_piano_roll.shape[0]

            if song_length > max_length:
                max_length = song_length
            if cover_length > max_length:
                max_length = cover_length
            training_data.append((song_piano_roll, cover_piano_roll))
            if count < 200:
                validation_data.append((song_piano_roll_val, cover_piano_roll_val))
            elif count < 400:
                testing_data.append((song_piano_roll_val, cover_piano_roll_val))
            
            count += 1

    training_data = extend(training_data, max_length)
    validation_data = extend(validation_data, max_length)
    testing_data = extend(testing_data, max_length)
    
    return training_data, validation_data, testing_data


def model_train(model, lr, batch_size, training_data, validation_data, num_epochs, device):
    torch.cuda.empty_cache()

    model = model.to(device)
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9)

    batch_size = batch_size
    train_loader = DataLoader(training_data, batch_size=batch_size, shuffle=True)

    validation_loader = DataLoader(validation_data, batch_size=batch_size, shuffle = True)


    train_loss = np.zeros(num_epochs)
    val_loss = np.zeros(num_epochs)


    for epoch in range(num_epochs):
        train_loss_total = 0.0
        val_loss_total = 0.0

        # Training
        model.train()
        count = 0
        for data in train_loader:
            count += 1
            songs = data[0].to(device)

            covers = data[1].to(device)
            optimizer.zero_grad()

            outputs = model(songs)

            
            loss = blur_loss(outputs, covers) + criterion(outputs, covers)
            loss.backward(retain_graph = True)
            optimizer.step()

            train_loss_total += loss.item()
            
            torch.cuda.empty_cache()

        checkpoint = {
        'epoch': epoch + 1,
        'state_dict': model.state_dict(),
        'optimizer': optimizer.state_dict(),
        # Add any other information you want to save (e.g., training loss, validation loss, etc.)
        }
        torch.save(checkpoint, f'checkpoint_epoch{epoch + 1}.pt')
        # Validation
        model.eval()
        with torch.no_grad():
            for data in validation_loader:
                images = data[0].to(device)

                labels = data[1].to(device)
                outputs = model(images)

                loss = criterion(outputs, labels)
                val_loss_total += loss.item()
        train_loss[epoch] = train_loss_total
        val_loss[epoch] = val_loss_total

        print(f'Epoch [{epoch+1}/{num_epochs}], '
                f'Train Loss: {train_loss_total:.4f}, Train Loss: {train_loss_total:.4f}, '
                f'Val Loss: {val_loss_total:.4f}, Val Loss: {val_loss_total:.4f}')
        torch.cuda.empty_cache()


    model_path = str(lr) + '_' + str(batch_size) + '_' + str(num_epochs)
    torch.save(model.state_dict(), 'model' + model_path)
    np.savetxt("{}_train_loss.csv".format(model_path), train_loss)
    np.savetxt("{}_val_loss.csv".format(model_path), val_loss)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model = Net(width = 10, batch_size = 1)

training_data, validation_data, testing_data = get_data()

train_loader = DataLoader(training_data, batch_size=1, shuffle=True)

for data in train_loader:
    model = model.to(device)
    out = model(data[0].to(device))
#model_train(model,1e-4, 2, training_data, validation_data, 1, device)