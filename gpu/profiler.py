import os
import time
import matplotlib.pyplot as plt
import sys
sys.path.append('../common')
from tools import *

import re
import csv
import pdb
import pandas as pd
import numpy as np

def extract_xy(s):
    """Extracts x and y from a string formatted as 'profile_<x>x<y>'."""
    match = re.search(r'profile_(\d+)x(\d+)', s)
    if match:
        x = int(match.group(1))  # Extracts the first number (x)
        y = int(match.group(2))  # Extracts the second number (y)
        return x, y
    else:
        raise ValueError("String does not match the required format 'profile_<x>x<y>'")

def group_rows_by_line_numbers(csv_file, line_numbers):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)
    
    # Filter the DataFrame for the rows where 'Line #' is in the list of line_numbers
    grouped_data = df[df['Line #'].isin(line_numbers)]

    return grouped_data


def parse_lprof_to_csv(input_file, output_file):
    with open(input_file, "r") as f:
        lines = f.readlines()

    data = []
    headers = ["Line #", "Hits", "Time (µs)", "Per Hit Time (µs)", "% Time", "Code"]
    
    parsing = False
    for line in lines:
        if "Line #" in line and "Hits" in line:
            parsing = True
            continue
        if parsing and line.strip() == "":
            break
        if parsing:
            # Regular expression to match lines with profiling data
            match = re.match(r"\s*(\d+)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(.*)", line)
            if match:
                data.append([
                    int(match.group(1)),  # Line #
                    int(match.group(2)),  # Hits
                    float(match.group(3)),  # Total Time
                    float(match.group(4)),  # Per Hit Time
                    float(match.group(5)),  # % Time
                    match.group(6).strip(),  # Code
                ])
    
    # Write to CSV
    with open(output_file, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)



max_x, max_y, k_sz = get_max_res_and_k_size()
res_list = get_test_resolutions(max_x, max_y, k_sz)


starting_x = 0.128
one_out_of = 4 # on tick out of ... 

for x, y in res_list:
    label = f'{x}x{y}'
    print(f"\nProfiling: {label}")
    txt_file = f'results/data/profiles/txt/profile_{label}.txt'
    # os.system(f"kernprof -l -v lif_snn_full.py -r -m test -l {x} -w {y} >> {txt_file}")
    # time.sleep(10)
    

path = 'results/data/profiles/txt/'

# List all files in the directory
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
io_data = []
cpu_to_gpu = []
launch = []
synchronization = []
input_size = []
for file in files:

    fname = file[:-4]
    txt_file = f'results/data/profiles/txt/{fname}.txt'
    csv_file = f'results/data/profiles/csv/{fname}.csv'
    parse_lprof_to_csv(txt_file, csv_file)
    x, y = extract_xy(fname)
    print(f"{fname} --> {x}x{y}")
    input_size.append(x*y)
    # continue

    # Example usage
    def_main_line = 300

    io_data_lines = [x + def_main_line for x in [45,47,58,60,61,64,71,72,74,75,78,86,87]]
    cpu_to_gpu_lines = [x + def_main_line for x in [48,53,54,55]]
    launch_lines =  [x + def_main_line for x in [50]]
    synchronization_lines =  [x + def_main_line for x in [51]]

    lines_sets = [io_data_lines, cpu_to_gpu_lines, launch_lines, synchronization_lines]
    sets_labels = ['IO Data', 'CPU <-> GPU', 'Launch', 'Synchronization']

    lat_grp_idx = -1
    for lines_set in lines_sets:
        lat_grp_idx += 1
        rows = group_rows_by_line_numbers(csv_file, lines_set)
        value = rows['Per Hit Time (µs)'].sum()/1000
        print(f"\t{sets_labels[lat_grp_idx]}: {value:.2f} ms")
        if sets_labels[lat_grp_idx] == 'IO Data':
            io_data.append(value)
        if sets_labels[lat_grp_idx] == 'CPU <-> GPU':
            cpu_to_gpu.append(value)
        if sets_labels[lat_grp_idx] == 'Launch':
            launch.append(value)
        if sets_labels[lat_grp_idx] == 'Synchronization':
            synchronization.append(value)

neural_algo = (8*np.ones(len(io_data))).tolist()
xtra_latency = [a+b+c+d for a, b, c, d in zip(io_data,cpu_to_gpu,launch,synchronization)]
full_latency = [a+b for a, b in zip(xtra_latency, neural_algo)]

if os.path.isfile("lif_snn_full.py.lprof"):
    os.system('rm lif_snn_full.py.lprof')


plt.figure(figsize=(int(24/one_out_of*(1-starting_x)), 4))

a = 0.5
msz = 20
plt.scatter(input_size, io_data, label='IO data', marker='p', color='#4C0099', alpha=a, s=30)
plt.scatter(input_size, cpu_to_gpu, label='CPU <-> GPU', marker='^', color='#4C0099', alpha=a, s=msz)
plt.scatter(input_size, launch, label='Launch', marker='+', color='#4C0099', alpha=a, s=30)
plt.scatter(input_size, synchronization, label='Synchronization', marker='o', color='#4C0099', alpha=a, s=msz)
plt.scatter(input_size, xtra_latency, label='GPU extra Latency', marker='*', color='#4C0099')
# plt.scatter(input_size, neural_algo, label='Neural Algorithms')
# plt.scatter(input_size, full_latency, label='Full Latency')

# plt.axvline(x=85*64, color='k', linestyle=':', linewidth=1)
# plt.axvline(x=153*104, color='k', linestyle=':', linewidth=1)
# plt.axvline(x=198*128, color='k', linestyle=':', linewidth=1)
# plt.axvline(x=256*165, color='k', linestyle=':', linewidth=1)

# plt.legend(ncol=1, loc='center right', bbox_to_anchor=(-0.2, 0.5), fontsize=10)
plt.legend()


plt.grid()


x_tick_labels = []
x_tick_locations =[]
res_idx = -1
for x, y in sorted(res_list):
    cur_tick_val = ''
    res_idx += 1
    nb_neurons = x*y
    max_nb_n = max_x*max_y
    ratio = (nb_neurons)/(max_nb_n)
    if  ratio >= starting_x:
        if res_idx%one_out_of==1:
            x_tick_locations.append(nb_neurons)
            cur_tick_val += f'{x}\nx\n{y}'
            if 0.55 < ratio < 0.65 or ratio <= starting_x*1.1 or ratio == 1:
                cur_tick_val += f'\n\n({math.ceil(ratio*100)}%)'
            else:
                cur_tick_val += f'\n\n'
            x_tick_labels.append(cur_tick_val)

plt.xlim([starting_x*max_nb_n, max_nb_n])    
plt.xticks(x_tick_locations, x_tick_labels)
plt.xlabel(f'\nSize of Input Layer (% of {max_x}x{max_y})')

ylim = 11
plt.ylim(-1,ylim)
plt.yticks(range(-1,ylim+1))
plt.ylabel('Latency [ms]')

plt.tight_layout()
plt.subplots_adjust(bottom=0.25) 

plt.savefig(f'results/images/nb_neurons_vs_latency_GPU.png', dpi=400)
