import socket
import struct
import time
import argparse
from threading import Thread

import sys
sys.path.append('../configuration')
from cfgparser import *
from spif_details import *




# Event counter
event_count = 0
scaler = 10


# Function to count events every second
def count_events():
    global event_count
    while True:
        time.sleep(1/scaler)
        if event_count > 50000/scaler:
            print(f"Events received in the last second: {scaler*event_count}")
        event_count = 0

# Function to receive data
def receive_data(host, port):

    BUFFER_SIZE = 4096  # Size of buffer for receiving data

    global event_count
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((host, port))
        print(f"Listening on {host}:{port}...")

        while True:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            # Calculate number of events (4 bytes per event)
            num_events = len(data) // 4
            event_count += num_events

def parse_args():

    HOST = '0.0.0.0'  # Listen on all network interfaces
    PORT = 3330

    parser = argparse.ArgumentParser(description="Event Counter")
    parser.add_argument('-p', '--port', type=int, help=f"Destination port number (default: {PORT})", default=PORT)
    parser.add_argument('-i', '--ip', type=str, help=f"Destination IP address (default: {HOST})", default=HOST)

    return parser.parse_args()


if __name__ == "__main__":
    
    args = parse_args()
    Thread(target=count_events, daemon=True).start()
    receive_data(args.ip, args.port)
