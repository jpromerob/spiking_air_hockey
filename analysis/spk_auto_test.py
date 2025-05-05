import os
from datetime import datetime
import time
import pdb
import random
import socket
import struct
import argparse


'''
This Script calls analyzer.py (SpiNNaker and GPU) using different combinations of stimulus speed/sparsity
'''


def generate_random_floats(offset_max):
    off_x = round(random.uniform(-offset_max, offset_max),2)
    off_y = round(random.uniform(-offset_max, offset_max),2)
    return off_x, off_y


def parse_args():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="SpiNNaker Auto Test")
    parser.add_argument('-x', '--length', type=int, help="Size X axis", default=0)
    parser.add_argument('-y', '--width', type=int, help="Size Y axis", default=0)
     
    return parser.parse_args()


if __name__ == '__main__':
    # Parse the arguments
    args = parse_args()
    length = args.length
    width = args.width

    speed_mapper = {
        "high": (0.47, 0.57, 4, 8)
    }
    
    nb_runs = 1
    nb_steps = 5
    nb_pts = 2100


    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 5555
    # Bind the socket to listen on the specified port
    sock.bind(("172.16.222.30", port))
    print(f"Listening for integers on port {port}...")

    while True:

        # Receive data from the sender
        data, addr = sock.recvfrom(1024)
        
        # Unpack the received bytes back into two integers
        length, width = struct.unpack('ii', data)

        print("\n************************************\n")
        print(f"New resolution :{length}x{width}")
        print("\n************************************\n")


        for speed in speed_mapper:
            print("\n\n\n*****************************************")
            print(f"Starting simulation for {speed} speed")
            print("*****************************************\n\n\n")
            min_sparsity = speed_mapper[speed][0]
            max_sparsity = speed_mapper[speed][1]
            min_delta = speed_mapper[speed][2]
            max_delta = speed_mapper[speed][3]

            for i in range(nb_steps):


                dname = f"Synthetic_{length}x{width}_{'high'}_{datetime.now().strftime('%y%m%d_%H%M%S')}"                
                sparsity = round(min_sparsity+i*(max_sparsity-min_sparsity)/nb_steps,3)
                delta = round(min_delta+i*(max_delta-min_delta)/nb_steps,3)
                print(f"Fname: {dname} | Sparsity: {sparsity} | Delta: {delta}")

                for j in range(nb_runs):

                    off_x, off_y = generate_random_floats(0.75)
                    go_right = random.randint(0, 1)
                    go_down = random.randint(0, 1)

                    fname = dname + f"_v{j+1}"

                    print(fname)
                    cmd = ''
                    cmd += f"python3 analyzer.py -do spk -n {nb_pts}"
                    # cmd += f" -s {random.uniform(0.37, 0.47)} -d {random.uniform(0.20, 0.28)} -f {fname}"
                    cmd += f" -s {sparsity} -d {delta/10} -f {fname} "
                    cmd += f" -ox {off_x} -oy {off_y} -gr {go_right} -gd {go_down}"
                    cmd += f" -m zigzag "
                    cmd += f" -l {length} -w {width}"

                    # RUN ON SPINNAKER
                    cmd += ""
                    print(cmd)
                    os.system(cmd)
                    time.sleep(5)

                    # # RUN ON GPU
                    # cmd += " -g"
                    # print(cmd)
                    # os.system(cmd)
                    # time.sleep(5)
        
                    
            




