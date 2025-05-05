import os
import csv
import time
import numpy as np
import multiprocessing
import subprocess
import socket
import struct
import argparse
import sys
sys.path.append('../common')
from tools import *



# Define a class to group the shared variables
class SharedValues:
    def __init__(self, args):
        self.max_x = args.max_x
        self.max_y = args.max_y
        self.k_size = args.k_size
        self.nb_pts = args.nb_pts
        self.pipeline = args.pipeline
        self.x_value = multiprocessing.Value('i', 0)
        self.y_value = multiprocessing.Value('i', 0)
        self.nn_value = multiprocessing.Value('i', 0)
        self.done_event = multiprocessing.Event()
        self.resolutions =  get_test_resolutions(args.max_x, args.max_y, args.k_size)
        if self.pipeline == 'gpu':
            self.script = f'lif_snn_full.py'
        else:
            self.script = 'convolutioner.py'

        print(f'Starting Resolution tests for {self.pipeline} pipeline using:')
        for x, y in self.resolutions:
            print(f'\t{x} x {y}')



'''
This function sends current resolution to CPU in charge of generating events
'''
def send_integers(x, y, ip="172.16.222.30", port=5555):
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Pack the integers into a binary format to send as bytes
    message = struct.pack('ii', x, y)
    
    # Send the packed message to the receiver
    sock.sendto(message, (ip, port))
    print(f"Sent integers: {x}, {y}")

    # Close the socket
    sock.close()

'''
This function calls nvidia-smi to get current GPU-core utilization
'''
def get_gpu_utilization(gpu_id):
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
        stdout=subprocess.PIPE,
        text=True
    )
    return int(result.stdout.splitlines()[gpu_id])  # GPU utilization for specified GPU

'''
This function calls nvidia-smi to get current GPU-memory utilization
'''
def get_mem_utilization(gpu_id):
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
        stdout=subprocess.PIPE,
        text=True
    )
    return int(result.stdout.splitlines()[gpu_id])  # Memory utilization for specified GPU


'''
This function launches the Neural Algorithm
'''
def run_snn(shared_values):

    for res in shared_values.resolutions:

        x, y = res  
        print(f"Starting with {x} x {y}")
        nb_neurons = 3*((x-32)*(y-32))+((x-32)*(y-32))+(x-32)+(y-32)
        
        # Update Share memories for resolution in x and y axes + number of instantiated neurons
        shared_values.x_value.value = x  
        shared_values.y_value.value = y  
        shared_values.nn_value.value = nb_neurons

        print(f'Launching SNN on {shared_values.pipeline}')        
        os.system(f"python3 ../{shared_values.pipeline}/{shared_values.script} -l {x} -w {y}")

        print(f"Done with {x} x {y}")
        time.sleep(5)

    # Notify that we are done launching all the SNNs needed
    shared_values.done_event.set() 


def log_stats_gpu(shared_values, gpu_id=1):

    file_name = f'../{shared_values.pipeline}/results/data/stats.csv'
    file_exists = os.path.isfile(file_name) and os.path.getsize(file_name) > 0

    with open(file_name, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header only if the file is new
        if not file_exists:
            writer.writerow(["x", "y", "nb_neurons", "gpu", "mem"])

        while not shared_values.done_event.is_set():

            time.sleep(25)
            
            x = shared_values.x_value.value
            y = shared_values.y_value.value
            nn = shared_values.nn_value.value

            ratio = (x*y)/(shared_values.max_x*shared_values.max_y)

            time.sleep(int(80*ratio))

            for i in range(5):
                gpu_val = get_gpu_utilization(gpu_id)
                mem_val = get_mem_utilization(gpu_id)
                writer.writerow([x, y, nn, gpu_val, mem_val])
                time.sleep(5)
            file.flush()  
            print(f"{x}x{y}px: {nn} neurons --> {gpu_val}% + {mem_val}MB")

            send_integers(x, y)

            time.sleep(240)
                    
            # Stop the `lif_snn_full.py` process if needed
            os.system(f"pkill -f {shared_values.script}")
            print("Killed SNN")
        
        print('Done!!!')
            

def log_stats_spinnaker(shared_values):

    file_name = f'../{shared_values.pipeline}/results/data/stats.csv'
    file_exists = os.path.isfile(file_name) and os.path.getsize(file_name) > 0

    with open(file_name, mode='a' if file_exists else 'w', newline='') as file:
        writer = csv.writer(file)
        # Write the header only if the file is new
        if not file_exists:
            writer.writerow(["x", "y", "nb_neurons", "cores", "mem"])

        while not shared_values.done_event.is_set():
            os.system(f'mv reports/* ../{shared_values.pipeline}/reports/')

            x = shared_values.x_value.value
            y = shared_values.y_value.value
            nn = shared_values.nn_value.value

            time.sleep(180)

            for i in range(5):
                cores_val = 0 #@TODO ideally this should come from reports ... but ... too much effort
                mem_val = 0 #@TODO ideally this should come from reports ... but ... too much effort
                writer.writerow([x, y, nn, cores_val, mem_val])
                time.sleep(5)
            file.flush()  
            print(f"{x}x{y}px: {nn} neurons --> {cores_val}% + {mem_val}MB")

            send_integers(x, y)
            
            time.sleep(240)


            os.system(f"pkill -f {shared_values.script}")
            print("Killed SNN")
        
        print('Done!!!')
            

def parse_args():

    parser = argparse.ArgumentParser(description='Testing SNN Accelerator with different Input Resolutions')

    max_x, max_y, k_size = get_max_res_and_k_size()

    parser.add_argument('-x', '--max-x', type= int, help="Max X resolution", default=max_x)
    parser.add_argument('-y', '--max-y', type=int, help="Max Y resolution", default=max_y)
    parser.add_argument('-k', '--k-size', type=int, help="Kernel Size", default=k_size)
    parser.add_argument('-n', '--nb-pts', type=int, help="# Points to record", default=30)
    parser.add_argument('-p', '--pipeline', type=str, help="Pipeline: spinnaker | gpu", default='gpu')

    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()


    # Create shared memories
    shared_values = SharedValues(args)

    # Create the processes
    snn_process = multiprocessing.Process(target=run_snn, args=(shared_values,))
    if shared_values.pipeline == 'gpu':
        stats_process = multiprocessing.Process(target=log_stats_gpu, args=(shared_values,))
    else:
        stats_process = multiprocessing.Process(target=log_stats_spinnaker, args=(shared_values,))


    # Start the processes
    snn_process.start()
    stats_process.start()

    # Wait for both processes to finish
    snn_process.join()
    stats_process.join()
