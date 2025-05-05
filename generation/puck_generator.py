import argparse
import time
import math
import socket
import random
import pdb
import multiprocessing

# Add necessary imports
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

def puck_generation_process(shared_data):

    time.sleep(0.100)

    dim = Dimensions.load_from_file('../common/homdim.pkl')
    indices = shared_data['indices']
    sparsity = round(shared_data['sparsity'],3)

    if shared_data['gpu']:
        print("Sending Data to GPU")
    else:
        print("Sending Data to SpiNNaker")

    
    global sock
    while(True):
        data = b""
        offset_x = shared_data['cx'] - int(shared_data['k_sz']/2)
        offset_y = shared_data['cy'] - int(shared_data['k_sz']/2)
        # print(f"Offsets: {offset_x},{offset_y}")
        max_nb_evs = len(indices)
        act_nb_events = int(sparsity*max_nb_evs)
        for i in np.random.choice(np.arange(max_nb_evs), size=act_nb_events, replace=False):      
            x = indices[i][1] + offset_x 
            y = indices[i][0] + offset_y 
            polarity = 1
            packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
            data += pack("<I", packed)

        sock.sendto(data, (shared_data['ip'], shared_data['port'])) # for Visualization
        if shared_data['gpu']:
            sock.sendto(data, (shared_data['gpu_ip'], 3333)) # for GPU pipeline
        else:
            sock.sendto(data, (shared_data['spinnaker_ip'], 3333)) # for SpiNNaker pipeline


        x_norm = shared_data['cy']/dim.fl*100
        y_norm = shared_data['cx']/dim.fw*100
        data = "{},{}".format(x_norm, y_norm).encode()
        sock.sendto(data, (shared_data['ip'], shared_data['in_time_port'])) 

        time.sleep(0.001)

def trajectory_process(shared_data):

    min_x = shared_data['k_sz']/2
    min_y = shared_data['k_sz']/2
    max_x = shared_data['width']-shared_data['k_sz']/2
    max_y = shared_data['height']-shared_data['k_sz']/2

    offx = shared_data['offx']
    offy = shared_data['offy']
    amplitude_x = 0.75-abs(offx)
    amplitude_y = 0.75-abs(offy)

    cx_0 = int(shared_data['width']/2)
    cy_0 = int(shared_data['height']/2)
    dx_dy_ratio = shared_data['dx_dy_ratio']

    delta = shared_data['delta']
    t = 0

    if shared_data['mode'] == 'line_x':
        go_right = shared_data['go_right']
    if shared_data['mode'] == 'line_y':
        go_down = shared_data['go_down']
    if shared_data['mode'] == 'zigzag':
        go_right = shared_data['go_right']
        go_down = shared_data['go_down']
        if dx_dy_ratio >= 1:
            dx = shared_data['delta']
            dy = dx/dx_dy_ratio
        else:
            dy = shared_data['delta']
            dx = dy*dx_dy_ratio



    delta_0 = round(delta*0.003,10)

    cx = cx_0*(1+offx)
    cy = cy_0*(1+offy)

    print(f"cx: {cx} | cy: {cy}")

    while(True):

        if shared_data['mode'] == 'line_x':
            if go_right:
                if cx + delta <= max_x:
                    cx += delta
                else:
                    go_right = False
                    cx -= delta
            if not go_right:
                if cx - delta >= min_x:
                    cx -= delta
                else:
                    go_right = True
                    cx += delta

        if shared_data['mode'] == 'line_y':
            if go_down:
                if cy + delta <= max_y:
                    cy += delta
                else:
                    go_down = False
                    cy -= delta
            if not go_down:
                if cy - delta >= min_y:
                    cy -= delta
                else:
                    go_down = True
                    cy += delta

        
        if shared_data['mode'] == 'zigzag':
            if go_right:
                if cx + dx <= max_x:
                    cx += dx
                else:
                    go_right = False
                    cx -= dx
            if not go_right:
                if cx - dx >= min_x:
                    cx -= dx
                else:
                    go_right = True
                    cx += dx
                    
            if go_down:
                if cy + dy <= max_y:
                    cy += dy
                else:
                    go_down = False
                    cy -= dy
            if not go_down:
                if cy - dy >= min_y:
                    cy -= dy
                else:
                    go_down = True
                    cy += dy

        if shared_data['mode'] == 'circle':
            cx = cx_0 + cx_0*(((math.sin(0.7*t+math.pi/3))*math.sin(0.4*t+math.pi/8)*math.sin(t))*amplitude_x)
            cy = cy_0 + cy_0*(((math.cos(0.3*t+math.pi/7))*math.cos(0.5*t+math.pi/4)*math.cos(t))*amplitude_y)



        shared_data['cx'] = int(cx) 
        shared_data['cy'] = int(cy) 
        t+=delta_0
        time.sleep(0.001)

    


def parse_args(pipeline_cfg):


    CPU_IP = pipeline_cfg['CPU']['IP']
    CPU_PORT = pipeline_cfg['Visualizers']['Raw_data']['Port']

    max_x, max_y, _ = get_max_res_and_k_size()

    parser = argparse.ArgumentParser(description="Script to call forward_data function every 100 microseconds.")
    parser.add_argument('-i', '--ip', type=str, help=f"Destination IP address (default: {CPU_IP})", default=CPU_IP)
    parser.add_argument('-p', '--port', type=int, help=f"Destination port number (default: {CPU_PORT})", default=CPU_PORT)
    parser.add_argument('-g','--gpu', action='store_true', help='Run on GPU!')
    parser.add_argument('-x', '--width',  type=int, help=f"Size X axis (default: {max_x})", default=max_x)
    parser.add_argument('-y', '--height', type=int, help=f"Size Y axis (default: {max_y})", default=max_y)
    parser.add_argument('-s', '--sparsity', type=float, help="Sparsity", default=0.2)
    parser.add_argument('-d', '--delta', type=float, help="Delta XY", default=0.2)
    parser.add_argument('-m', '--mode', type=str, help="mode", default="circle")
    parser.add_argument('-ox', '--offx', type=float, help="Offset X (percentage)", default=0)
    parser.add_argument('-oy', '--offy', type=float, help="Offset Y (percentage)", default=0)
    parser.add_argument('-gr', '--right', type=float, help="Go Right", default=1)
    parser.add_argument('-gd', '--down', type=float, help="Go Down", default=1)
    parser.add_argument('-xyr', '--xyratio', type=float, help="X-Y ratio in ZigZag", default=1)


    return parser.parse_args()


if __name__ == "__main__":
    
    pipeline_cfg = load_config('../configuration/pipeline.yaml')

    args = parse_args(pipeline_cfg)

    shared_data = multiprocessing.Manager().dict()


    shared_data['ip'] = args.ip
    shared_data['port'] = args.port
    shared_data['gpu'] = args.gpu # gpu_flag

    shared_data['width'] = args.width
    shared_data['height'] = args.height

    shared_data['mode'] = args.mode

    shared_data['cx'] = 0
    shared_data['cy'] = 0

    shared_data['sparsity'] = args.sparsity
    shared_data['delta'] = args.delta

    shared_data['offx'] = args.offx
    shared_data['offy'] = args.offy
    shared_data['go_right'] = args.right
    shared_data['go_down'] = args.down

    shared_data['dx_dy_ratio'] = args.xyratio

    shared_data['kernel'] = np.load("../common/fast_kernel.npy")
    shared_data['indices'] = np.argwhere(shared_data['kernel']==shared_data['kernel'].max())
    shared_data['k_sz'] = len(shared_data['kernel'])
    
    DEFAULT_CONVOLUTIONER_IP = pipeline_cfg['SNN_Accelerator']['SpiNNaker']['Convolutioner']['IP']
    DEFAULT_HOST_BOARD = int(DEFAULT_CONVOLUTIONER_IP.split('.')[-1])
    DEFAULT_HOST_IN_SPIF = spin_spif_map[f'{DEFAULT_HOST_BOARD}']

    shared_data['spinnaker_ip'] = DEFAULT_HOST_IN_SPIF
    shared_data['gpu_ip'] = pipeline_cfg['SNN_Accelerator']['GPU']['IP']
    shared_data['in_time_port'] = pipeline_cfg['Analyzer']['In_Time_Data']['Port']

    ev_gen_proc = multiprocessing.Process(target=puck_generation_process, args=(shared_data,))
    ev_gen_proc.start()

    traj_proc = multiprocessing.Process(target=trajectory_process, args=(shared_data,))
    traj_proc.start()

    ev_gen_proc.join()
    traj_proc.join()    
