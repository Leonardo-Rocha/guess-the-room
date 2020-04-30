#!/usr/bin/python3
# This file is used to scan the wifi data and parse 30 times.
# The filepath must be changed manually according to the room and time of the day.
# It generates a {filepath.csv} file where every row is in the form: 
# i, ssid_1, quality_1, signal_1, channel_1, ..., ssid_n, signal_n, channel_n
# where i varies from 0 to 29 and n depends on the wifi scan.
from wifi import Cell
import csv
import time

filepath = 'rooms-data/kitchen-morning.csv'

# Opens a csv file
with open(filepath, 'w', newline='') as csvfile:
    filewriter = csv.writer(csvfile, quotechar=' ', quoting=csv.QUOTE_MINIMAL)

    # do 30 readings with 5 seconds of delay between each one
    for i in range(30):
        # find all valid cells in the network device 'wlp3s0'
        valid_cell = 0
        cells_list = Cell.all('wlp3s0')
        while valid_cell == 0:
            cells_list = Cell.all('wlp3s0')
            # check if the cell is valid
            for cell in cells_list:
                valid_cell = 1
                break

        # Initialize an empty row
        row = [f'{i}, ']

        # loop through the cells appending in the row list
        
        for cell in cells_list:
            row[0] += f'{cell.ssid}, {cell.quality}, {cell.signal}, {cell.channel}, '
        
        # write in the csv
        filewriter.writerow(row)

        # wait 5 seconds
        time.sleep(5)
