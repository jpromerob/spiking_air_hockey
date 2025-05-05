import os
from datetime import datetime
import time
import pdb
import random


'''
This Script calls analyzer.py (SpiNNaker and GPU) using different combinations of stimulus speed/sparsity
'''

def generate_random_floats(offset_max):
    off_x = round(random.uniform(-offset_max, offset_max),2)
    off_y = round(random.uniform(-offset_max, offset_max),2)
    return off_x, off_y

# min_sparsity, max_sparsity, min_delta, max_delta
speed_mapper = {
    "low": (0.12, 0.24, 0.4, 1),
    "medium": (0.28, 0.36, 1.8, 3),
    "high": (0.4, 1, 4, 8),
}

nb_runs = 5
nb_steps = 10
nb_pts = 2100


for speed in speed_mapper:
    print("\n\n\n*****************************************")
    print(f"Starting simulation for {speed} speed")
    print("*****************************************\n\n\n")
    min_sparsity = speed_mapper[speed][0]
    max_sparsity = speed_mapper[speed][1]
    min_delta = speed_mapper[speed][2]
    max_delta = speed_mapper[speed][3]

    for i in range(nb_steps):

        dname = f"Synthetic_{speed}_{datetime.now().strftime('%y%m%d_%H%M%S')}"

        sparsity = round(min_sparsity+i*(max_sparsity-min_sparsity)/nb_steps,3)

        delta = round(min_delta+i*(max_delta-min_delta)/nb_steps,3)
        print(f"Fname: {dname} | Sparsity: {sparsity} | Delta: {delta}")

        for j in range(nb_runs):

            off_x, off_y = generate_random_floats(0.75)
            go_right = random.randint(0, 1)
            go_down = random.randint(0, 1)

            print(f"\n\n{speed} run #{i+1}.{j+1}/{nb_steps}")

            fname = dname + f"_v{j+1}"

            print(fname)
            cmd = ''
            cmd += f"python3 analyzer.py -do syn -n {nb_pts} "
            cmd += f"-s {sparsity} -d {delta/10} -f {fname} "
            cmd += f"-ox {off_x} -oy {off_y} -gr {go_right} -gd {go_down} "
            cmd += f"-m zigzag "

            # RUN ON SPINNAKER
            cmd += ""
            print(cmd)
            os.system(cmd)
            time.sleep(5)

            # RUN ON GPU
            cmd += "-g"
            print(cmd)
            os.system(cmd)
            time.sleep(5)
            
        




