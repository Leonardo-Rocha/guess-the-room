#!/usr/bin/python3
import csv
import os
from scipy import stats
import numpy as np
from wifi import Cell

data_dict = dict()

"""
Loop through the files in the rooms-data classifying in a dict and normalizing 
the data.
"""
def train():
    directory = 'rooms-data'

    for filename in os.listdir(directory):
        # Opens a csv file
        full_path = os.path.join(directory, filename) 
        with open(full_path, 'r', newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')

            # the class name should be a room
            class_full = filename.split('-')
            class_name = class_full[0]
            
            for row in csvreader:
                signal_array = []
                channel_array = []

                # normalize the data
                # start from 1 to skip the index and walk 4 in 4 to parse the 
                # data of a single SSID
                for i in range(1, len(row) - 1, 4):
                    # the quality is not needed because it's obtained 
                    # from the signal
                    signal_array.append(int(row[i+2]))
                    channel_array.append(int(row[i+3]))

                # calculate the zscore for every attribute
                signal_zscores  = stats.zscore(signal_array)
                channel_zscores = stats.zscore(channel_array)

                attributes = []

                # this is used to access the elements of the zscores arrays
                zscore_index = 0
                for i in range(1, len(row) - 1, 4):
                    # SSID
                    attributes.append(row[i].strip())
                    # append the normalized attributes
                    attributes.append(signal_zscores[zscore_index])
                    attributes.append(channel_zscores[zscore_index])
                    # update the zscore_index
                    zscore_index += 1

                # creates the list if it doesn't exist yet
                if class_name not in data_dict:
                    data_dict[class_name] = []
                # put the data in the dict
                data_dict[class_name].append(attributes)


"""
Normalize the input(in-place) using zscore
Where input is a list = [ssid_1, signal_1, channel_1, ..., ssid_n, signal_n, channel_n]
"""
def normalize_input(input):
    signal_array = []
    channel_array = []
    for i in range(0, len(input)-1, 3):
        signal_array.append(int(input[i+1]))
        channel_array.append(int(input[i+2]))

    # calculate the zscore for every attribute
    signal_zscores  = stats.zscore(signal_array)
    channel_zscores = stats.zscore(channel_array)
    zscore_index = 0
    for i in range(0, len(input)-1, 3):
        input[i+1] = signal_zscores[zscore_index]
        input[i+2] = channel_zscores[zscore_index]
        zscore_index += 1


"""
Calculates the euclidean distance between two points in the space.
Where each argument is a list = [SSID, signal, channel]
"""
def euclidean_distance(source, destiny):
    ret = 0

    x_1 = source[0]
    y_1 = source[1]
    z_1 = source[2]

    x_2 = destiny[0]
    y_2 = destiny[1]
    z_2 = destiny[2]

    if x_1 != x_2:
        ret = 1

    ret += np.power(y_2 - y_1, 2) + np.power(z_2 - z_1, 2)

    return np.sqrt(ret)


"""
Finds the k-nearest-neighbor of a given input.
Where input is a list = [ssid_1, signal_1, channel_1, ..., ssid_n, signal_n, channel_n]

returns a tuple (class_name, probability)
"""
def k_nearest_neighbor(k, input):
    k_dict = dict()
    output_dict = dict()
    
    normalize_input(input)

    # loop through every class
    for class_name, attributes_matrix in data_dict.items():
        distances_array = []
        # loop through the attributes matrix
        for attributes in attributes_matrix:
            # for every ssid in the input search the according ssid
            for i in range(0, len(input)-1, 3):
                source_ssid    = input[i]
                source_signal  = input[i+1]
                source_channel = input[i+2]
                source = [source_ssid, source_signal, source_channel]
                
                for j in range(0, len(attributes) - 1, 3):
                    destiny_ssid = attributes[j]
                    # if the ids match compute the distance, otherwise do nothing
                    if source_ssid == destiny_ssid:
                        destiny_signal  = attributes[j+1]
                        destiny_channel = attributes[j+2]
                        destiny = [destiny_ssid, destiny_signal, destiny_channel]

                        distance = euclidean_distance(source, destiny)
                        # don't add repeated distances
                        if distance not in distances_array:
                            distances_array.append(distance)
        distances_array = np.sort(distances_array)
        for i in range(k):
            if 0 <= i < len(distances_array):
                k_dict[distances_array[i]] = class_name
    
    # get the k smallest distances and count appearances
    k_dict = sorted(k_dict.items())
    for i in range(k):
        item = k_dict[i]
        key = item[1]
        if key in output_dict:
            output_dict[key] += 1
        else:
            output_dict[key] = 1

    # get the one with the highest number of appearances and 
    # calculate the probability
    highest_appearances = 0
    ret = ()
    for item in output_dict.items():
        if item[1] > highest_appearances:
            highest_appearances = item[1]
            
            ret = (item[0], highest_appearances/k)

    return ret


def get_room_data():
    # initialize an empty room_data
    room_data = []

    # find all valid cells in the network device 'wlp3s0'
    valid_cell = 0
    cells_list = Cell.all('wlp3s0')
    while valid_cell == 0:
        cells_list = Cell.all('wlp3s0')
        # check if the cell is valid
        for cell in cells_list:
            valid_cell = 1
            break

    for cell in cells_list:
        room_data.append(cell.ssid)
        room_data.append(cell.signal)
        room_data.append(cell.channel)

    return room_data


if __name__ == '__main__':
    train()
    input = get_room_data()
    output = k_nearest_neighbor(11, input)

    print(f'You\'re in the {output[0]} with probability {round(output[1] * 100, 2)}')
