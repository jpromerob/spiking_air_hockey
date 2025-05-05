import numpy as np
import pyNN.spiNNaker as p
import pdb
import os
import socket
from struct import pack
import socket
import argparse
import time
import sys
import pdb
sys.path.append('../common')
from tools import *
from utils import *


sys.path.append('../configuration')
from cfgparser import load_config
from spif_details import *

#################################################################################################################
#                             SPINNAKER (+ SPIF) CONFIGURATION CHANGES (VS DEFAULT)                             #
#################################################################################################################

SPIF_IP_F = "172.16.223.2"      # SPIF-00 CHIP (0,0)
SPIF_IP_M = "172.16.223.130"    # SPIF-16 CHIP (16,8)
SPIF_IP_S = "172.16.223.122"    # SPIF-15 CHIP (32,16) 

CHIP_F = (0, 0)
CHIP_M = (16, 8)
CHIP_S = (32, 16)



#################################################################################################################
#                                       PIPELINE CONFIGURATION SETTINGS                                         #
#################################################################################################################

pipeline_cfg = load_config('../configuration/pipeline.yaml')

# IP for CPU (where visualization and manipulator control occur)
DEFAULT_CPU_IP = pipeline_cfg['CPU']['IP']

# IP for neural algorithms involved
DEFAULT_CONVOLUTIONER_IP = pipeline_cfg['SNN_Accelerator']['SpiNNaker']['Convolutioner']['IP']
DEFAULT_MAPPER_IP = pipeline_cfg['SNN_Accelerator']['SpiNNaker']['Mapper']['IP']
DEFAULT_HOST_BOARD = int(DEFAULT_CONVOLUTIONER_IP.split('.')[-1])
DEFAULT_HOST_IN_SPIF = spin_spif_map[f'{DEFAULT_HOST_BOARD}']
DEFAULT_NEXT_BOARD = DEFAULT_MAPPER_IP.split('.')[-1]
DEFAULT_NEXT_IN_SPIF = spin_spif_map[f'{DEFAULT_NEXT_BOARD}']

if DEFAULT_HOST_IN_SPIF not in [SPIF_IP_F, SPIF_IP_M, SPIF_IP_S]:
    print("The Inupt SPIF does not make sense")
    quit()
else:
    if DEFAULT_HOST_IN_SPIF == SPIF_IP_F:
        CHIP_I = CHIP_F # input through SPIF-00
    elif DEFAULT_HOST_IN_SPIF == SPIF_IP_M:
        CHIP_I = CHIP_M # input through SPIF-16
    elif DEFAULT_HOST_IN_SPIF == SPIF_IP_S:
        CHIP_I = CHIP_S # input through SPIF-15
    else:
        print("Something is odd with the SPIF-CHIP configuration")
        quit()
    
SPIF_IP_I = DEFAULT_HOST_IN_SPIF


# IPs for visualization purposes
DEFAULT_VIS_F_SCNN_PORT = pipeline_cfg['Visualizers']['Fast_SCNN']['Port']
DEFAULT_VIS_M_SCNN_PORT = pipeline_cfg['Visualizers']['Medium_SCNN']['Port']
DEFAULT_VIS_S_SCNN_PORT = pipeline_cfg['Visualizers']['Slow_SCNN']['Port']
DEFAULT_VIS_POST_CONVOLUTIONER_PORT = pipeline_cfg['Visualizers']['Post_Convolutioner']['Port']


# UDP_IP = pipeline_cfg['CPU']['IP']
print(f"DEFAULT_CPU_IP: {DEFAULT_CPU_IP}")
print(f"DEFAULT_HOST_BOARD: {DEFAULT_HOST_BOARD}")
print(f"DEFAULT_HOST_IN_SPIF: {DEFAULT_HOST_IN_SPIF}")
print(f"DEFAULT_NEXT_BOARD: {DEFAULT_NEXT_BOARD}")
print(f"DEFAULT_NEXT_IN_SPIF: {DEFAULT_NEXT_IN_SPIF}")
print(f"DEFAULT_VIS_F_SCNN_PORT: {DEFAULT_VIS_F_SCNN_PORT}")
print(f"DEFAULT_VIS_M_SCNN_PORT: {DEFAULT_VIS_M_SCNN_PORT}")
print(f"DEFAULT_VIS_S_SCNN_PORT: {DEFAULT_VIS_S_SCNN_PORT}")
print(f"DEFAULT_VIS_POST_CONVOLUTIONER_PORT: {DEFAULT_VIS_POST_CONVOLUTIONER_PORT}")
print(f"SPIF_IP_I: {SPIF_IP_I}")
print(f"CHIP_I: {CHIP_I}")




#################################################################################################################
#                                               ARGUMENT PARSING                                                #
#################################################################################################################

def parse_args():

    parser = argparse.ArgumentParser(description='Automatic Coordinate Location')


    max_x, max_y, _ = get_max_res_and_k_size()
    parser.add_argument('-l', '--length', type=int, help="Image length", default=max_x)
    parser.add_argument('-w', '--width', type=int, help="Image width", default=max_y)
    parser.add_argument('-ks', '--ks', type=int, help="Kernel Size", default=45)
    parser.add_argument('-ws', '--w-scaler', type=float, help="Weight Scaler", default=1.65) 
    parser.add_argument('-th', '--thickness', type=int, help="Kernel edge thickness", default=2)
    parser.add_argument('-r', '--ratio', type=float, help="f/s ratio", default=1.0) # 
    parser.add_argument('-rt', '--runtime', type=int, help="Runtime in [m]", default=300)
    return parser.parse_args()

#################################################################################################################
#                                                    MAIN                                                       #
#################################################################################################################

if __name__ == '__main__':

    args = parse_args()
    

    dim = Dimensions.load_from_file('../common/homdim.pkl')
    print("Setting machines up ... ")
    
    CFG_FILE = f"spynnaker_{DEFAULT_HOST_BOARD}.cfg"


    usr = input("Type username: ")
    pwd = input("Type password: ")
                
    print("Generating Kernels ... \n")
    f_kernel = make_whole_kernel("fast", args.ks, dim.hs, args.w_scaler, args.thickness, 1.8, usr, pwd)  
    m_kernel = make_whole_kernel("medium", args.ks, dim.hs, args.w_scaler, args.thickness, 0.9, usr, pwd)
    s_kernel = make_whole_kernel("slow", args.ks, dim.hs, args.w_scaler, args.thickness, 0.4, usr, pwd)  


    k_sz = len(f_kernel)

    print("Configuring Infrastructure ... ")
    SUB_WIDTH = 16
    SUB_HEIGHT = 8
    WIDTH = args.length
    HEIGHT = args.width
    OUT_WIDTH = WIDTH-len(f_kernel)+1
    OUT_HEIGHT = HEIGHT-len(f_kernel)+1


    nb_brd_req = 24
    nb_cores = nb_brd_req * 48 * 16
        
    NPC_X = 4
    NPC_Y = 2


    used_nb_neurons = 3*((WIDTH-len(f_kernel)+1)*(HEIGHT-len(f_kernel)+1))
    used_nb_cores = int(used_nb_neurons/(NPC_X*NPC_Y))
    percentage_use = round(100*used_nb_cores/nb_cores,2)

    print(f"Using {used_nb_neurons} neurons i.e. {used_nb_cores}/{nb_cores} cores ({percentage_use} % of the system)")
    time.sleep(2)

    
    POP_LABEL = "target"
    RUN_TIME = 1000*60*args.runtime
   


    P_SHIFT = 15
    Y_SHIFT = 0
    X_SHIFT = 16
    NO_TIMESTAMP = 0x80000000


    global sock 
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def forward_data(spikes, ip, port):
        global sock
        data = b""
        np_spikes = np.array(spikes)
        for i in range(np_spikes.shape[0]):      
            x = int(int(np_spikes[i]) % OUT_WIDTH)+int(k_sz/2)
            y = int(int(np_spikes[i]) / OUT_WIDTH)+int(k_sz/2)
            polarity = 1
            packed = (NO_TIMESTAMP + (polarity << P_SHIFT) + (y << Y_SHIFT) + (x << X_SHIFT))
            data += pack("<I", packed)
        sock.sendto(data, (ip, port))
        sock.sendto(data, (DEFAULT_NEXT_IN_SPIF, DEFAULT_IN_SPIF_PORT))
        sock.sendto(data, (DEFAULT_CPU_IP, DEFAULT_VIS_POST_CONVOLUTIONER_PORT)) 

    def forward_f_cnn_data(label, spikes):
        forward_data(spikes, DEFAULT_CPU_IP, DEFAULT_VIS_F_SCNN_PORT)

    def forward_m_cnn_data(label, spikes):
        forward_data(spikes, DEFAULT_CPU_IP, DEFAULT_VIS_M_SCNN_PORT)

    def forward_s_cnn_data(label, spikes):
        forward_data(spikes, DEFAULT_CPU_IP, DEFAULT_VIS_S_SCNN_PORT)

    print("Creating Network ... ")

    # Define common parameters
    common_neuron_params = {
        'tau_syn_E': 1.0,
        'tau_syn_I': 1.0,
        'v_rest': -65.0,
        'v_reset': -65.0,
        'v_thresh': -60.0,
        'tau_refrac': 0.0,
        'cm': 1,
        'i_offset': 0.0
    }




    p.setup(timestep=1.0, n_boards_required=nb_brd_req, cfg_file=CFG_FILE)


    celltype = p.IF_curr_exp
    p.set_number_of_neurons_per_core(celltype, (NPC_X, NPC_Y))


    ENABLE_F_SCNN = True
    ENABLE_M_SCNN = True
    ENABLE_S_SCNN = True


    #########################################################################################################
    #                                               Input Layer                                             #
    #########################################################################################################

    # Setting up SPIF Input
    IN_POP_LABEL = "input_a"
    p_spif_virtual_a = p.Population(WIDTH * HEIGHT, p.external_devices.SPIFRetinaDevice(
                                    pipe=0, width=WIDTH, height=HEIGHT,
                                    sub_width=SUB_WIDTH, sub_height=SUB_HEIGHT, 
                                    chip_coords=CHIP_I), label=IN_POP_LABEL)


    #########################################################################################################
    #                                               Fast SCNN                                               #
    #########################################################################################################

    if ENABLE_F_SCNN:

        # Setting up Fast (high-speed) Convolutional Layer
        F_CNN_POP_LABEL = "f_cnn"

        # Define specific parameters for different cell types
        f_cell_params = {'tau_m': 1, **common_neuron_params}

        # Define Convolutional Connector
        f_cnn_conn = p.ConvolutionConnector(kernel_weights=f_kernel)
        f_cnn_pop = p.Population(OUT_WIDTH * OUT_HEIGHT, celltype(**f_cell_params),
                                structure=p.Grid2D(OUT_WIDTH / OUT_HEIGHT), label=F_CNN_POP_LABEL)

        # Create Projections from Input Layer to Convolutional Layer
        p.Projection(p_spif_virtual_a, f_cnn_pop, f_cnn_conn, p.Convolution())

        # Send spikes from Convolutional Layer out (through SPIF)
        spif_f_lsc = p.external_devices.SPIFLiveSpikesConnection([F_CNN_POP_LABEL], SPIF_IP_F, DEFAULT_OUT_SPIF_PORT)
        spif_f_lsc.add_receive_callback(F_CNN_POP_LABEL, forward_f_cnn_data)
        spif_f_cnn_output = p.Population(None, p.external_devices.SPIFOutputDevice(
            database_notify_port_num=spif_f_lsc.local_port, chip_coords=CHIP_F), label="f_cnn_output")
        p.external_devices.activate_live_output_to(f_cnn_pop, spif_f_cnn_output)




    #########################################################################################################
    #                                           Medium-Speed SCNN                                           #
    #########################################################################################################

    
    if ENABLE_M_SCNN:
        
        # Setting up Mid (medium-speed) Convolutional Layer
        M_CNN_POP_LABEL = "m_cnn"

        # Define specific parameters for different cell types
        m_cell_params = {'tau_m': 12, **common_neuron_params}

        # Define Convolutional Connector
        m_cnn_conn = p.ConvolutionConnector(kernel_weights=m_kernel)
        m_cnn_pop = p.Population(OUT_WIDTH * OUT_HEIGHT, celltype(**m_cell_params),
                                structure=p.Grid2D(OUT_WIDTH / OUT_HEIGHT), label=M_CNN_POP_LABEL)

        # Create Projections from Input Layer to Convolutional Layer
        p.Projection(p_spif_virtual_a, m_cnn_pop, m_cnn_conn, p.Convolution())

        # Send spikes from Convolutional Layer out (through SPIF)
        spif_m_lsc = p.external_devices.SPIFLiveSpikesConnection([M_CNN_POP_LABEL], SPIF_IP_M, DEFAULT_OUT_SPIF_PORT)
        spif_m_lsc.add_receive_callback(M_CNN_POP_LABEL, forward_m_cnn_data)
        spif_m_cnn_output = p.Population(None, p.external_devices.SPIFOutputDevice(
            database_notify_port_num=spif_m_lsc.local_port, chip_coords=CHIP_M), label="m_cnn_output")
        p.external_devices.activate_live_output_to(m_cnn_pop, spif_m_cnn_output)




    #########################################################################################################
    #                                               Slow SCNN                                               #
    #########################################################################################################


    if ENABLE_S_SCNN:

        # Setting up Slow (low-speed) Convolutional Layer
        S_CNN_POP_LABEL = "s_cnn"

        # Define specific parameters for different cell types
        s_cell_params = {'tau_m': 64, **common_neuron_params}

        # Define Convolutional Connector
        s_cnn_conn = p.ConvolutionConnector(kernel_weights=s_kernel)
        s_cnn_pop = p.Population(OUT_WIDTH * OUT_HEIGHT, celltype(**s_cell_params),
                                structure=p.Grid2D(OUT_WIDTH / OUT_HEIGHT), label=S_CNN_POP_LABEL)

        # Create Projections from Input Layer to Convolutional Layer
        p.Projection(p_spif_virtual_a, s_cnn_pop, s_cnn_conn, p.Convolution())

        # Send spikes from Convolutional Layer out (through SPIF)
        spif_s_lsc = p.external_devices.SPIFLiveSpikesConnection([S_CNN_POP_LABEL], SPIF_IP_S, DEFAULT_OUT_SPIF_PORT)
        spif_s_lsc.add_receive_callback(S_CNN_POP_LABEL, forward_s_cnn_data)
        spif_s_cnn_output = p.Population(None, p.external_devices.SPIFOutputDevice(
            database_notify_port_num=spif_s_lsc.local_port, chip_coords=CHIP_S), label="s_cnn_output")
        p.external_devices.activate_live_output_to(s_cnn_pop, spif_s_cnn_output)


    #########################################################################################################
    #                                                Summary                                                #
    #########################################################################################################

    try:
        time.sleep(1)
        print("List of parameters:")
        print(f"Board 172.16.223.{DEFAULT_HOST_BOARD} ({CFG_FILE})")
        print(f"SPIF @ {SPIF_IP_I}")
        print(f"\tNPC: {NPC_X} x {NPC_Y}")
        print(f"\tInput {WIDTH} x {HEIGHT}")
        print(f"\tOutput {OUT_WIDTH} x {OUT_HEIGHT}")
        print(f"\tKernel Size: {len(f_kernel)}")
        print(f"\tKernel Sum: {abs(round(np.sum(f_kernel),3))}")
        print(f"\tWeight Scaler: {args.w_scaler}")
        print(f"\tSending to {DEFAULT_NEXT_IN_SPIF} through {DEFAULT_IN_SPIF_PORT}")


        user_input = input_with_timeout("Happy?\n ", 10)
    except KeyboardInterrupt:
        print("\n Simulation cancelled")
        quit()


    RIG_POWER_IP = f'172.16.223.{0}'
    print(f"Waiting for rig-power ({RIG_POWER_IP}) to end ... ")    
    os.system(f"rig-power {RIG_POWER_IP}")
    
    p.run(RUN_TIME)

    p.end()

