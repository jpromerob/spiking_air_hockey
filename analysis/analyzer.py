import aestream
import numpy as np
import time
import torch
import torch.nn as nn
import sys
import multiprocessing
import argparse
import pdb
import os


import warnings
warnings.filterwarnings("ignore", message="Unable to import Axes3D")
import matplotlib.pyplot as plt

sys.path.append('../common')
from tools import Dimensions

from com_analyzer import *
from spif_details import *


sys.path.append('../configuration')
from cfgparser import load_config

#################################################################################################################
#                                       PIPELINE CONFIGURATION SETTINGS                                         #
#################################################################################################################

pipeline_cfg = load_config('../configuration/pipeline.yaml')

# IP for CPU (where visualization and manipulator control occur)


DEFAULT_CPU_IP = pipeline_cfg['CPU']['IP']
DEFAULT_GPU_IP = pipeline_cfg['SNN_Accelerator']['GPU']['IP']
DEFAULT_SPINNAKER_IP = pipeline_cfg['SNN_Accelerator']['SpiNNaker']['Convolutioner']['IP']
DEFAULT_SPIF_IP = spin_spif_map[f'{DEFAULT_SPINNAKER_IP.split(".")[-1]}']



def gen_ev_process(shared_data):

    cmd =""
    cmd += f"python3 ../generation/puck_generator.py "
    cmd += f" -s {shared_data['sparsity']} -d {shared_data['delta']}"
    cmd += f" -ox {shared_data['offx']} -oy {shared_data['offy']}"
    cmd += f" -m {shared_data['gmode']}"
    cmd += f" -x {shared_data['res_x']} -y {shared_data['res_y']}"

    if shared_data['gpu']:
        print("Launch event generation for GPU")
        cmd += f" -g"
    else:
        print("Launch event generation for SpiNNaker")
        cmd += f""
    
    print(cmd)
    os.system(cmd)


def initialize_shared_data(args):

    shared_data = multiprocessing.Manager().dict()
    
    shared_data['CPU_IP'] = DEFAULT_CPU_IP
    shared_data['GPU_IP'] = DEFAULT_GPU_IP
    shared_data['SPIF_IP'] = DEFAULT_SPIF_IP

    dim = Dimensions.load_from_file('../common/homdim.pkl')
    shared_data['hs'] = dim.hs

    if args.length > 0 and args.length > 0:
        shared_data['res_x'] = args.length
        shared_data['res_y'] = args.width
    else:
        shared_data['res_x'] = dim.fl # length
        shared_data['res_y'] = dim.fw # width

    shared_data['fname'] = args.fname 

    shared_data['offx'] = args.offx
    shared_data['offy'] = args.offy

    shared_data['delta'] = args.delta
    shared_data['sparsity'] = args.sparsity
    shared_data['gpu'] = args.gpu
    shared_data['data_origin'] = args.dorigin
    shared_data['nb_frames'] = args.nb_frames
    shared_data['gmode'] = args.gmode

    shared_data['done_storing_data'] = False
    shared_data['intime_pose'] = (0,0)
    shared_data['delayed_pose'] = (0,0)

    shared_data['port'] = args.port

    return shared_data


def parse_args():

    parser = argparse.ArgumentParser(description='Display From AEstream')

    parser.add_argument('-n', '--nb-frames', type= int, help="Max number of frames", default=2000)
    parser.add_argument('-f', '--fname', type= str, help="File Name", default="synthetic")
    parser.add_argument('-g','--gpu', action='store_true', help='Run on GPU!')
    parser.add_argument('-p', '--port', type= int, help="Port for events coming from GPU|SpiNNaker", default=5050)

    parser.add_argument('-do', '--dorigin', type= str, help="Data Origin: syn|rec|gpu|spk", default="syn")

    parser.add_argument('-m', '--gmode', type= str, help="Generation Mode", default="circle")
    parser.add_argument('-s', '--sparsity', type= float, help="Sparsity", default=0.6)
    parser.add_argument('-d', '--delta', type= float, help="Delta (puck speed)", default=3.0)
    parser.add_argument('-ox', '--offx', type=float, help="Offset X (percentage)", default=0)
    parser.add_argument('-oy', '--offy', type=float, help="Offset Y (percentage)", default=0)
    parser.add_argument('-gr', '--right', type=float, help="Go Right", default=1)
    parser.add_argument('-gd', '--down', type=float, help="Go Down", default=1)
    parser.add_argument('-l', '--length', type= int, help="Manual Resolution x-axis (length)", default=0)
    parser.add_argument('-w', '--width', type= int, help="Manual Resolution y-axis (width)", default=0)

    return parser.parse_args()



if __name__ == '__main__':

    args = parse_args()

    shared_data = initialize_shared_data(args)

    if shared_data['data_origin'] == "rec":

        # Process to stream real-world events (AEstream)
        ae_proc = multiprocessing.Process(target=aestream_process, args=(shared_data,))
        ae_proc.start()

    else:

        # Process to generate synthetic events
        genev_proc = multiprocessing.Process(target=gen_ev_process, args=(shared_data,))
        genev_proc.start()

        # Process to 'store' Ground Truth
        intime_proc = multiprocessing.Process(target=intime_process, args=(shared_data,))
        intime_proc.start()
    
    # Process to 'store' Tracking 'Truth'
    delayed_proc = multiprocessing.Process(target=delayed_process, args=(shared_data,))
    delayed_proc.start()


    ground_truth_process(shared_data)

    delayed_proc.join()  
    if shared_data['data_origin'] == "rec":
        ae_proc.join() 
    else:
        genev_proc.join()
        intime_proc.join()   
 

