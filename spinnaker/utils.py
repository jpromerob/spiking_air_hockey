import numpy as np
import math
import paramiko
import select
import sys
import pdb
import csv
import matplotlib.pyplot as plt


sys.path.append('../configuration')
from cfgparser import load_config



#################################################################################################################
#                                       PIPELINE CONFIGURATION SETTINGS                                         #
#################################################################################################################

pipeline_cfg = load_config('../configuration/pipeline.yaml')

# IP for CPU (where visualization and manipulator control occur)
DEFAULT_CPU_IP = pipeline_cfg['CPU']['IP']
DEFAULT_GPU_IP = pipeline_cfg['SNN_Accelerator']['GPU']['IP']




##############################################################################################
# In this script, fast CNN inhibits slow CNN
##############################################################################################

def save_tuples_to_csv(data, filename):
    """
    Save a list of tuples to a CSV file.

    Args:
        data (list of tuples): The data to be saved.
        filename (str): The name of the CSV file to create or overwrite.
    """
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerow(row)

def create_conn_list(width, height):
    delay = 0.1 # [ms]
    weight = 56
    conn_list = []
    for idx in range(width*height):
        pre_idx = idx
        x = int(idx % width)
        y = int(idx / width)

        post_idx = x
        conn_list.append((pre_idx, post_idx, weight, delay))
        post_idx = width + y
        conn_list.append((pre_idx, post_idx, weight, delay))

    save_tuples_to_csv(conn_list, "my_conn_list.csv")
    return conn_list

def create_one_to_one_cnn_2d(w, h, npc_x, npc_y):
    conn_list = []    
    weight = 24
    delay = 0.1 # 1 [ms]
    nb_col = math.ceil(w/npc_x)
    nb_row = math.ceil(h/npc_y)

    pre_idx = -1
    for h_block in range(nb_row):
        for v_block in range(nb_col):
            for row in range(npc_y):
                for col in range(npc_x):
                    x = v_block*npc_y+col
                    y = h_block*npc_x+row
                    if x<w and y<h:
                        pre_idx += 1                       
                        conn_list.append((pre_idx, x, weight, delay))
                        conn_list.append((pre_idx, w+y, weight, delay))
        
    save_tuples_to_csv(conn_list, "my_conn_list.csv")
    return conn_list

def input_with_timeout(prompt, timeout):
    print(prompt, end='', flush=True)
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    
    if rlist:
        return sys.stdin.readline().strip()
    else:
        return None

def send_kernel(ip_out, kernel_file, username, password):
    # Define the connection parameters
    hostname = ip_out  # IP address or hostname of Computer B
    port = 22  # Default SSH port is 22

    # Define the local add remote file paths
    local_file_path = f'../common/{kernel_file}' 
    remote_file_path = input('Path to destination on Remote PC: ')+f'/common/{kernel_file}'  


    # Create an SSH client
    ssh_client = paramiko.SSHClient()

    # Automatically add the server's host key (this is insecure, see note below)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the remote server
    ssh_client.connect(hostname, port, username, password)

    # Use SFTP to copy the file from Computer A to Computer B
    with ssh_client.open_sftp() as sftp:
        sftp.put(local_file_path, remote_file_path)

    # Close the SSH connection
    ssh_client.close()

    # print(f"File '{local_file_path}' copied to '{remote_file_path}' on {hostname}")

def make_kernel_circle(r, k_sz, weight, kernel):
    
    var = int((k_sz+1)/2-1)
    a = np.arange(0, 2 * math.pi, 0.01)
    dx = np.round(r * np.sin(a)).astype("uint32")
    dy = np.round(r * np.cos(a)).astype("uint32")
    kernel[var + dx, var + dy] = weight

def make_whole_kernel(name, k_sz, hs, w_scaler, thickness, fs_ratio, usr, pwd):

    # Kernel size should be 'odd' (not 'even')
    k_sz = int(k_sz*hs)
    if k_sz%2 == 0:
        k_sz += 1

    # Radius of pattern edges (target)
    pos_radi = np.array([20,10])*hs
    neg_radi = np.array([2,3,14,15])*hs

    # pos_w is given by the w_scaler
    pos_w = w_scaler*fs_ratio/k_sz

    # Try Kernel WITHOUT negative values 'first'
    kernel = np.zeros((k_sz, k_sz), dtype=np.float32)
    for r in pos_radi:
        for i in np.arange(r-thickness+1, r+1):
            make_kernel_circle(i, k_sz, pos_w, kernel)
    for r in neg_radi:
        for i in np.arange(r-thickness+1, r+1):
            make_kernel_circle(i, k_sz, -pos_w, kernel)

    # Check positive values so as to compensate for them
    total_positive = np.sum(kernel)
    count_positive = np.sum(kernel != 0)

    # neg_w is estimated to compensate for pos_w
    neg_w = -total_positive/((k_sz*k_sz)-count_positive)

    # Try Kernel WITH negative values
    kernel = neg_w*np.ones((k_sz, k_sz), dtype=np.float32)
    for r in pos_radi:
        for i in np.arange(r-thickness+1, r+1):
            make_kernel_circle(i, k_sz, pos_w, kernel) 
    for r in neg_radi:
        for i in np.arange(r-thickness+1, r+1):
            make_kernel_circle(i, k_sz, -pos_w, kernel)
            
    import matplotlib.colors as mcolors
    from mpl_toolkits.axes_grid1 import make_axes_locatable


    cmap = mcolors.ListedColormap(['black', 'white', '#00B050'])


    fig, ax = plt.subplots()

    k_heatmap = ax.imshow(kernel, interpolation='nearest', cmap='binary')
    
    min_val = kernel.min()
    max_val = kernel.max()


    divider = make_axes_locatable(ax)
    cax = divider.append_axes("bottom", size="5%", pad=0.5)

    colorbar = plt.colorbar(k_heatmap, cax=cax, orientation='horizontal')
    colorbar.set_label('Weight Scale')
    # colorbar.set_ticks([min_val, 0, max_val])
    ax.set_xticks(range(33))
    ax.set_yticks(range(33))
    ax.set_xlim([-0.5,32.5])
    ax.set_ylim([-0.5,32.5])
    ax.grid(True)


    plt.savefig(f"../spinnaker/images/{name}_kernel.png")
    plt.clf()


    np.save(f"../common/{name}_kernel.npy", kernel)
    
    send_kernel(DEFAULT_CPU_IP, f"{name}_kernel.npy", usr, pwd)
    send_kernel(DEFAULT_GPU_IP, f"{name}_kernel.npy", usr, pwd)

    print(f"Kernel '{name}':")
    print(f"\tPositive weights: {round(pos_w,6)}")
    print(f"\tNegative weights: {round(neg_w,6)}")
    print("\n")
        

    return kernel

def div_eight(original_nb):
    new_nb = math.ceil(original_nb/8)*8
    return new_nb

# def set_kernels():
