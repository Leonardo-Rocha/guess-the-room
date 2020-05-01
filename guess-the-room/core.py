#!/usr/bin/python3
import csv
import os
from scipy import stats
import numpy as np

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
            attributes_matrix = []
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

                attributes_matrix.append(attributes)
                
            # put the data in the dict
            # TODO: if the class_name already exists update the matrix
            data_dict[class_name] = attributes_matrix


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
                
                for i in range(0, len(attributes) - 1, 3):
                    destiny_ssid = attributes[i]
                    # if the ids match compute the distance, otherwise do nothing
                    if source_ssid == destiny_ssid:
                        destiny_signal  = attributes[i+1]
                        destiny_channel = attributes[i+2]
                        destiny = [destiny_ssid, destiny_signal, destiny_channel]

                        distance = euclidean_distance(source, destiny)

                        distances_array.append(distance)
        distances_array = np.sort(distances_array)
        for i in range(k):
            k_dict[distances_array[i]] = class_name
    
    for key, value in sorted(k_dict):
        output_dict[value] += key / k

    highest_value = 0
    ret = ()
    for item in output_dict.items():
        if item.value > highest_value:
            highest_value = item.value
            ret = item

    return ret


if __name__ == '__main__':
    train()
    input = ['Asgard', '-84', '10', 'Almeida', '-72', '11']
    output = k_nearest_neighbor(3, input)

    print(output)
