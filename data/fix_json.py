import json
import copy

file_path = 'songs.json'

with open(file_path, "r") as json_file:
    existing_data = json.load(json_file)

songs = existing_data["songs"]

new_data = copy.copy(existing_data)


offset_found = False
num_433 = 0
for i in range(len(songs)):
    song_filename = songs[i]["filename"]
    song_num = int(song_filename.split("_")[0])

    if song_num == 433:
        num_433 += 1
    
    if num_433 == 2:
        offset_found = True

    if offset_found:
        new_data["songs"][i]["filename"] = str(song_num + 14) + "_song" + '.wav'
        for j in  range (len(new_data["songs"][i]["piano covers"]["filename"])):
            new_data["songs"][i]["piano covers"]["filename"][j] = str(song_num + 14) + '_' +str(j) + "_cover" + '.wav'

with open(file_path, "w") as json_file:
    json.dump(new_data, json_file, indent=4)