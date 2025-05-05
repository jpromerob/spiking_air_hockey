import pandas as pd
import matplotlib.pyplot as plt
import re
import random
import math
import numpy as np
from scipy.ndimage import gaussian_filter1d
import pdb
import sys

sys.path.append('../common')
from tools import *

def get_random_color():
    return (random.random(), random.random(), random.random())


# Parse 'Recording' to extract X and Y
def parse_recording(recording):
    match = re.search(r'Synthetic_(\d+)x(\d+)_high', recording)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

# Remove outliers within each X*Y group (e.g., values beyond 2 standard deviations)
def remove_outliers(group, k=1.5):
    mean = group['Latency'].mean()
    std = group['Latency'].std()
    return group[(group['Latency'] >= mean - k * std) & (group['Latency'] <= mean + k * std)]


def from_pandas_to_numpy(grouped):
    values = []
    labels = ['X*Y', 'mean', 'std']

    # Add extra value at end of series
    for label in labels:

        if label == 'std':
            extra_value = grouped[label].iloc[-1]
        else:
            extra_value = 2 * grouped[label].iloc[-1] - grouped[label].iloc[-2]

        # Append the new value to the series using pd.concat
        series = pd.concat([grouped[label], pd.Series([extra_value])], ignore_index=True)

        # Convert the updated series to a NumPy array
        values.append(series.to_numpy())

    return values[0], values[1], values[2]


def get_data(pipeline, k_out, g_sigma):
    
    if pipeline == 'spinnaker':
        pipeline = 'spk'

    # Load CSV data
    df = pd.read_csv(f'results/{pipeline}_summary_ok.csv')

    df['X'], df['Y'] = zip(*df['Recording'].map(parse_recording))

    # Keep necessary columns and create a copy to avoid SettingWithCopyWarning
    df = df[['X', 'Y', 'Latency', 'Error', 'MinError']].copy()

    
    df = df[~((df['X'].isin(range(0,189))) & (df['Latency'] < 9*0.75))]
    df = df[~((df['X'].isin(range(0,189))) & (df['Latency'] > 9*1.25))]

    # Calculate X * Y
    df['X*Y'] = df['X']*df['Y']

    # Remove outliers
    # df = df.groupby('X*Y', group_keys=False,).apply(remove_outliers).reset_index(drop=True)
    df = df.groupby('X*Y', group_keys=False).apply(lambda group: remove_outliers(group, k=k_out)).reset_index(drop=True)


    # Group by X*Y and calculate mean and standard deviation of Latency for plotting
    grouped = df.groupby('X*Y')['Latency'].agg(mean='mean', std='std').reset_index()


    x_values, mean_values, std_values = from_pandas_to_numpy(grouped)

    
    # Apply Gaussian filter with a standard deviation to control smoothness
    mean_values = gaussian_filter1d(mean_values, sigma=g_sigma)  # Adjust sigma as needed
    std_values = gaussian_filter1d(std_values, sigma=g_sigma)

    return df, x_values, mean_values, std_values


    

if __name__ == '__main__':

    legend_out_up = True
    starting_x = 0.128
    one_out_of = 4 # on tick out of ... 
    k_out = 2
    g_sigma = 0.6

    gpu_df, gpu_x_values, gpu_mean_values, gpu_std_values = get_data('gpu', k_out, g_sigma)
    spk_df, spk_x_values, spk_mean_values, spk_std_values = get_data('spinnaker', k_out, g_sigma)



    # Plot the mean line and the standard deviation envelope
    plt.figure(figsize=(int(24/one_out_of*(1-starting_x)), 4))

    color_gpu = '#4C0099'
    color_spinnaker = '#006666'



    plt.fill_between(spk_x_values, spk_mean_values - spk_std_values, spk_mean_values + spk_std_values, color=color_spinnaker, alpha=0.3)
    plt.scatter(spk_df['X*Y'], spk_df['Latency'], color=color_spinnaker, alpha=0.1, s=5)
    plt.plot(spk_x_values, spk_mean_values, color=color_spinnaker, label='SpiNNaker')
    
    
    plt.fill_between(gpu_x_values, gpu_mean_values - gpu_std_values, gpu_mean_values + gpu_std_values, color=color_gpu, alpha=0.3)
    plt.scatter(gpu_df['X*Y'], gpu_df['Latency'], color=color_gpu, alpha=0.1, s=5)
    plt.plot(gpu_x_values, gpu_mean_values, color=color_gpu, label='GPU')
    
    
    max_x, max_y, k_sz = get_max_res_and_k_size()
    res_list = get_test_resolutions(max_x, max_y, k_sz)
    print(res_list)
    x_tick_labels = []
    x_tick_locations =[]
    idx = -1
    for x, y in sorted(res_list):
        cur_tick_val = ''
        idx += 1
        nb_neurons = x*y
        max_nb_n = max_x*max_y
        ratio = (nb_neurons)/(max_nb_n)
        if  ratio >= starting_x:
            if idx%one_out_of==1:
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

    plt.ylabel('Latency [ms]')
    plt.yticks(range(0, 21,1))
    # plt.yticks(sorted(list(range(0, 21, 2)) + [9]))
    if legend_out_up:
        plt.legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.2), fontsize=10)  # Increase fontsize as needed
        plt.tight_layout()  # Adjusts layout to fit everything
    else:    
        plt.legend()
    plt.ylim([4,20])

    # Activate grid on both x and y axes
    plt.grid(True)
    gpu_better_than_spk_until_x = 0.554
    # plt.axvline(x=0.54*max_nb_n, color='k', linestyle=':', linewidth=0.5)
    plt.axvline(x=gpu_better_than_spk_until_x*max_nb_n, color='k', linestyle=':', linewidth=0.5)
    plt.text(
        gpu_better_than_spk_until_x*max_nb_n, 5.2,  # Coordinates (x=10.5, y=15)
        f'{gpu_better_than_spk_until_x*100:.0f}% → ',  # Text content
        fontsize=7,
        ha='right'
    )

    # Customize y-axis grid to show every second tick
    ax = plt.gca()  # Get current axis
    ax.xaxis.grid(True)  # Enable x-axis grid
    ax.yaxis.grid(True, which='both') 
    # ax.text(0.31, 1.04, 'Resolutions', transform=ax.transAxes)
    plt.tight_layout()

    plt.subplots_adjust(bottom=0.35)  # Increase the value to create more space

    # Save the plot
    plt.savefig('results/images/summary/nb_neurons_vs_latency.png', dpi=400)
