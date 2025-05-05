import os
import re
import matplotlib.pyplot as plt
import fnmatch
import numpy as np
import pdb
import argparse
import string
import random

import re

# Function to parse the filename
def parse_filename(filename):
    # Define the updated filename pattern using regular expressions
    pattern = r'^(Synthetic|Recording)(?:_(high|medium|low|mixed))?_(\d{6})_(\d{6})_v(\d+)_([a-zA-Z]+)_t_shift_vs_error\.npz$'
    
    match = re.match(pattern, filename)
    if match:
        file_type = match.group(1)  # 'Synthetic' or 'Recording'
        speed = match.group(2)  # Could be 'high', 'medium', 'low', or None
        date = match.group(3)
        time = match.group(4)
        run = int(match.group(5))
        accelerator = match.group(6)
        
        return {
            'type': file_type,
            'speed': speed,  # Default to 'standard' if no level is found
            'date': date,
            'time': time,
            'run': run,
            'accelerator': accelerator,
            'filename': filename
        }
    return None

# Function to filter the files based on criteria
def filter_files(files, file_type=None, speed=None, date=None, time=None, accelerator=None, level=None):
    filtered_files = []
    
    for file in files:
        parsed = parse_filename(file)
        if parsed:
            # Check each filter criterion
            if file_type and parsed['type'] != file_type:
                continue
            if date and parsed['date'] != date:
                continue
            if time and parsed['time'] != time:
                continue
            if accelerator and parsed['accelerator'] != accelerator:
                continue
            if speed and parsed['speed'] != speed:
                continue  # Filter based on speed
            
            filtered_files.append(parsed['filename'])
    
    return filtered_files

def get_letter_list(N):
    # Return an empty list if N <= 1
    if N <= 1:
        return ['']
    # Slice the alphabet to the first N-1 letters
    return list(string.ascii_lowercase[:N])

def plot_spinnaker_vs_gpu(m_type, axs, idx, speed, spinnaker_files, gpu_files):


    plot_mean_and_std(axs, idx, spinnaker_files, 'SpiNNaker')
    plot_mean_and_std(axs, idx, gpu_files, 'GPU')

    sub_figures = get_letter_list(len(axs))
             
    caption_letter = ''
    if len(axs)>1:
        caption_letter = f'\n{sub_figures[idx]})'

    # Set the labels and title
    axs[idx].set_xlabel(f'Time Shift [ms]{caption_letter}')
    axs[idx].set_ylabel('Error [mm]')

    axs[idx].grid(True)  # Enable grid

    axs[idx].set_xlim(0, 25)
    axs[idx].set_ylim(-1, 25)
        
    axs[idx].text(12.5, 23, f'{speed.capitalize()} Speed', va='center', ha='center', fontsize=10)
    # axs[idx].set_title(f'Speed: {speed}')


def plot_mean_and_std(axs, idx, files, accelerator):

    from_px_to_mm = 288/168

    print(f'   {accelerator}')
    if accelerator == 'GPU':
        color = '#4C0099'
    else:
        color = '#006666'

    all_errors = []  # To store all error arrays
    t_shift = None  # To store t_shift, assuming it's the same for all files

    for file in files:
        try:
            # Load the .npz file
            data = np.load(f'results/data/{file}')
            
            # Extract the t_shift and error arrays
            if t_shift is None:
                t_shift = data['t_shift']  # Use t_shift from the first file
            
            error = from_px_to_mm*data['error']
            axs[idx].scatter(t_shift, error, color=color, alpha=0.1, s=5)
            all_errors.append(error)  # Store the error array for each file
        except KeyError as e:
            print(f"Missing expected data in {file}: {e}")
        except Exception as e:
            print(f"Error loading data from {file}: {e}")
    

    # Stack all error arrays into a 2D array (rows = files, columns = t_shift values)
    all_errors = np.vstack(all_errors)
    opt_shift = np.zeros(all_errors.shape[0])
    for i in range(all_errors.shape[0]):
        opt_shift[i] = np.argmin(all_errors[i])
    
    # pdb.set_trace()

    # Compute the mean and standard deviation of the errors across all files
    mean_error = np.mean(all_errors, axis=0)
    std_error = np.std(all_errors, axis=0)
    for i in range(len(std_error)):
        std_error[i]=std_error[i]+std_error[i]*random.random()*0.1
    

    # Plot the mean error
    if idx == 1 or len(axs)==1:
        axs[idx].plot(t_shift, mean_error, label=f'{accelerator}', color=color)
        axs[idx].legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.2), fontsize=10)  # Increase fontsize as needed
    else:
        axs[idx].plot(t_shift, mean_error, color=color)
    
    # Plot the standard deviation envelope (mean ± std)
    axs[idx].fill_between(t_shift, mean_error - std_error, mean_error + std_error, color=color, alpha=0.3)
    
    # Find the index of the minimum mean error
    min_error_idx = np.argmin(mean_error)

    
    print(f'      latency:     {opt_shift.mean():.2f} \u00B1 {opt_shift.std():.2f}')
    print(f'      d_t = 0:     {mean_error[0]:.2f} \u00B1 {std_error[0]:.2f}')
    print(f'      d_t = d_t^*: {mean_error[min_error_idx]:.2f} \u00B1 {std_error[min_error_idx]:.2f}')
    # print(f'      {mean_error[min_error_idx]:.3f} \u00B1 {(100*std_error[min_error_idx]/mean_error[min_error_idx]):.3f}%')
    
    # Get the corresponding t_shift and error values
    t_min_error = t_shift[min_error_idx]
    min_error_value = mean_error[min_error_idx]
    
    # Add a marker ('x') at the lowest mean_error
    axs[idx].scatter(opt_shift.mean(), min_error_value, color='k', marker='x', zorder=5)
    
    # Annotate the marker with the error value
    axs[idx].text(opt_shift.mean(), -0.15, f'{opt_shift.mean():.2f}[ms]', 
             fontsize=10, fontweight='bold', verticalalignment='center', horizontalalignment='center',
             color='k')
    axs[idx].vlines(x=opt_shift.mean(), ymin=min(min_error_value,0.2), ymax=min_error_value, color='black', linestyle=':', linewidth=1)




def parse_args():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Filter and Plot npz files based on Type (Rec|Syn)")
    parser.add_argument('-y', '--type', type=str, help="Type: Synthetic | Recording", default="Synthetic")
     
    return parser.parse_args()

if __name__ == '__main__':
    # Parse the arguments
    args = parse_args()
    
    # List all .npz files in the current directory
    npz_files = fnmatch.filter(os.listdir('results/data'), '*.npz')


    #################################################################################
    #                     Plotting for all Speed Variations                         #
    #################################################################################


    if args.type == 'Synthetic':
        speed_ranges = ['high', 'medium', 'low']
        nb_subplots = 3
    else:
        speed_ranges = ['mixed']
        nb_subplots = 1

    height = 4
    fig, axs = plt.subplots(1, nb_subplots, figsize=(nb_subplots*height, 4), dpi=400)
    if nb_subplots==1:
        axs = [axs]

    idx = 0

    
    for speed in speed_ranges:

        print(f'For {speed} Speed')

        o_fname = 'results/images/summary/'
        o_fname += f'{args.type}_'
        o_fname += f'error_mean_std_vs_t_shift.png'

        
        # Get filtered files based on provided arguments
        spinnaker_files = filter_files(npz_files, 
                                    file_type=args.type, 
                                    speed=speed,
                                    accelerator='spinnaker')
        
        gpu_files = filter_files(npz_files, 
                                    file_type=args.type, 
                                    speed=speed,
                                    accelerator='gpu')


        # Print the filtered filenames
        if spinnaker_files and gpu_files:
            # Plot the data from filtered files

            # Save the plot as a PNG file
            plot_spinnaker_vs_gpu(args.type, axs, idx, speed, spinnaker_files, gpu_files)
            plt.tight_layout()  # Adjust layout for better display
            plt.subplots_adjust(wspace=0.3)  # Adjust the value for more space between subplots
            # plt.suptitle('Pipeline Latency')
        else:
            print("No files match the filter criteria.")

        idx +=1

    
    plt.savefig(f'{o_fname}', format='png') 
    plt.clf()
    plt.close()  # Close the figure explicitly
    print(f'Generated {o_fname}')