#!/usr/bin/python3
# This file is used to scan the wifi data and parse 30 times.
# The room and time_of_day must be changed manually according to the room and time of the day.
# It generates a {filename}.csv file where every row is in the form:
# i, ssid_1, quality_1, signal_1, channel_1, ..., ssid_n, signal_n, channel_n
# where i varies from 0 to 29 and n depends on the wifi scan.
# NOTE: it doesn't work if you're connected in a wifi.
from wifi import Cell
import csv
import time

folder = "rooms-data/"
room = "kitchen"
time_of_day = "night"

filepath = f"{folder}{room}-{time_of_day}.csv"

# Opens a csv file
with open(filepath, "w", newline="") as csvfile:
    filewriter = csv.writer(csvfile, quotechar=" ", quoting=csv.QUOTE_MINIMAL)

    print(f"Collecting data for the {room} in the {time_of_day}.")

    # do 30 scans with 5 seconds of delay between each one
    for i in range(30):
        # find all valid cells in the network device 'wlp3s0'
        valid_cell = 0
        cells_list = Cell.all("wlp3s0")
        while valid_cell == 0:
            cells_list = Cell.all("wlp3s0")
            # check if the cell is valid
            for cell in cells_list:
                valid_cell = 1
                break

        # Initialize an empty row
        row = [f"{i}, "]

        # loop through the cells appending in the row list
        for cell in cells_list:
            row[
                0
            ] += (
                f"{cell.ssid}, {cell.quality}, {cell.signal}, {cell.channel}, "
            )

        # write in the csv
        filewriter.writerow(row)
        print(f"Scan {i} done!")

        # so we doesn't wait in the last scan
        if i < 29:
            print("Next scan in: ")
            # wait 5 seconds
            for i in range(5, 0, -1):
                print(i)
                time.sleep(1)
            print()

    print("Room scanning done!")
