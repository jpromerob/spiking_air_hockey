
import pandas as pd
import numpy as np
import math
import argparse
from scipy.interpolate import interp1d

# This script produces numpy arrays with interpolated data based on *.csv with sparse datapoints

def parse_args():

    parser = argparse.ArgumentParser(description='Trajectory Creator')
    parser.add_argument('-f', '--filename', type=str, help="Filename", default="")
    parser.add_argument('-m', '--mode', type=str, help="clean|wavy", default="clean")


    return parser.parse_args()


if __name__ == '__main__':


    args = parse_args()

    if args.filename == "":
        print("No data points provided")
        quit()

    # Read data from CSV file
    df = pd.read_csv(f'{args.filename}')

    # Extracting data from DataFrame
    original_t = df.iloc[:, 0].values
    original_x = df.iloc[:, 1].values
    original_y = df.iloc[:, -1].values

    if args.mode == "wavy":
        fraction = 0.8
        frequency = 0.6
        sin_waveform = np.sin(frequency*original_t)
        original_x[0:int(len(original_x)*fraction)] = sin_waveform[0:int(len(original_x)*fraction)]*10

    # Interpolation
    t = np.linspace(original_t.min(), original_t.max(), 1000)
    f_x = interp1d(original_t, original_x, kind='cubic')
    f_y = interp1d(original_t, original_y, kind='cubic')
    puck_x = f_x(t)
    puck_y = f_y(t)


    base_name = args.filename.rsplit('.', 1)[0]

    out_f_name = f'{base_name}_{args.mode}.npz'
    print(out_f_name)
    np.savez(out_f_name, t=t, puck_x=puck_x, puck_y=puck_y)