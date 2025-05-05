import argparse
import sched
import time
import socket
import numpy as np
from struct import pack

import sys

sys.path.append('../common')
from tools import *

sys.path.append('../configuration')
from cfgparser import *
from spif_details import *


global sock 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Define your function here
def forward_data(spikes, ip, port, width):
    global sock
    data = b""
    np_spikes = np.array(spikes)
    for i in range(np_spikes.shape[0]):      
        x = int(np_spikes[i] % width)
        y = int(np_spikes[i] / width)
        polarity = 1
        packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
        data += pack("<I", packed)
    sock.sendto(data, (ip, port))


def coordinate_generator(length, width):
    while(True):
        for y in range(width):
            for x in range(length):
                for i in range(10):
                    yield x, y

def parse_args():

    pipeline_cfg = load_config('../configuration/pipeline.yaml')
    CPU_IP = pipeline_cfg['CPU']['IP']
    CPU_PORT = pipeline_cfg['Visualizers']['Raw_data']['Port']

    
    max_x, max_y, _ = get_max_res_and_k_size()

    parser = argparse.ArgumentParser(description="Event Generator")
    parser.add_argument("-ip", type=str, default=CPU_IP, help=f"Destination IP address (default: {CPU_IP})")
    parser.add_argument("-port", type=int, default=CPU_PORT, help=f"Destination port number (default: {CPU_PORT})")
    parser.add_argument("-x", type=int, default=max_x, help=f"Size X axis (default: {max_x})")
    parser.add_argument("-y", type=int, default=max_x, help=f"Size Y axis (default: {max_y})")

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    ip = args.ip
    port = args.port
    length = args.x
    width = args.y

    gen = coordinate_generator(length, width)

    while(True):

        x, y = next(gen)
        spikes = [y*length+x]  # Replace with your data
        forward_data(spikes, ip, port, length)
        time.sleep(0.001)
