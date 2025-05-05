import pandas as pd
import numpy as np
import pdb
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy.interpolate import make_interp_spline
from scipy.stats import linregress


import argparse

class LR_Result:
    def __init__(self, slope, intercept, r_value, p_value, stderr):
        self.slope = slope
        self.intercept = intercept
        self.rvalue = r_value
        self.pvalue = p_value
        self.stderr = stderr

def parse_args():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Filter and Plot npz files based on Type (Rec|Syn)")
    parser.add_argument('-y', '--type', type=str, help="Type: Synthetic | Recording", default="Synthetic")
     
    return parser.parse_args()

if __name__ == '__main__':
    # Parse the arguments
    args = parse_args()
    

    # Save the combined plot
    if args.type == 'Synthetic':
        type_label = 'syn'
        speed_src = 'MaxSpeed'
    if args.type == 'Recording':
        type_label = 'rec'
        speed_src = 'MeanSpeed'
    # Load the CSV file into a DataFrame
    df = pd.read_csv(f'results/{type_label}_summary_ok.csv')  # Replace 'your_file.csv' with the actual filename

    PLOT_SPLINE = False


    # Get unique pipelines
    unique_pipelines = df['Pipeline'].unique()

    # Create subplots for the three plots
    fig, axs = plt.subplots(1, 3, figsize=(12, 4), dpi=400)

    # Define colors and labels for each pipeline
    colors = {
        'spinnaker': '#006666',
        'gpu': '#4C0099'
    }
    labels = {
        'spinnaker': 'SpiNNaker',
        'gpu': 'GPU'
    }

    scaled_speed = []
    nb_points = 1000000

    # Aggregate data and plot for each unique pipeline
    for pipeline in unique_pipelines:
        # Filter data for the current pipeline
        pipeline_data = df[df['Pipeline'] == pipeline]

        # Aggregate by MaxSpeed, taking the mean of the other columns
        aggregated_data = pipeline_data.groupby(speed_src).agg({
            'Latency': 'mean',
            'Error': 'mean',
            'MinError': 'mean'
        }).reset_index()


        from_px_to_m = 0.288/168
        from_px_to_mm = 1000*from_px_to_m
        speed_scaler = (from_px_to_m)/0.001  # 28cm = 0.28m --> 164 pixels in 0.001 seconds

        lim_lm = 0.15*speed_scaler
        lim_mh = 0.37*speed_scaler
        x_low = 0.08*speed_scaler
        x_medium = 0.26*speed_scaler
        x_high = 0.64*speed_scaler
        f_sz = 8

        scaled_speed = aggregated_data[speed_src] * speed_scaler

        print(f"{pipeline}")
        nb_points = min(nb_points, len(scaled_speed))


    plot_regressor = False
    plot_x_max = 1.6
    x = [0, plot_x_max]
    lin_reg_params = []
    # Aggregate data and plot for each unique pipeline
    for pipeline in unique_pipelines:
        # Filter data for the current pipeline
        pipeline_data = df[df['Pipeline'] == pipeline]

        # Aggregate by Speed, taking the mean of the other columns
        aggregated_data = pipeline_data.groupby(speed_src).agg({
            'Latency': 'mean',
            'Error': 'mean',
            'MinError': 'mean'
        }).reset_index()

        # Scatter and interpolate for Latency
        axs[0].scatter(scaled_speed[:nb_points-1], aggregated_data['Latency'][:nb_points-1], color=colors[pipeline], s=10, alpha=0.5, label=labels[pipeline])  # No legend for this plot
        lin_reg_params.append([pipeline, 'Latency', LR_Result(0,np.mean(aggregated_data['Latency'][:nb_points-1]),0,0,0)])
        if plot_regressor:
            m = lin_reg_params[-1][2].slope
            b = lin_reg_params[-1][2].intercept
            y = [m * xi + b for xi in x]
            axs[0].plot(x, y, color='k', linewidth=1)

        # Scatter and interpolate for Error
        axs[1].scatter(scaled_speed[:nb_points-1], from_px_to_mm*aggregated_data['Error'][:nb_points-1], color=colors[pipeline], s=10, alpha=0.5, label=labels[pipeline])  # No legend for this plot
        lin_reg_params.append([pipeline,'Error',  linregress(scaled_speed[:nb_points-1], from_px_to_mm*aggregated_data['Error'][:nb_points-1])])
        if plot_regressor:    
            m = lin_reg_params[-1][2].slope
            b = lin_reg_params[-1][2].intercept
            y = [m * xi + b for xi in x]
            axs[1].plot(x, y, color='k', linewidth=1)

        # Scatter and interpolate for MinError
        axs[2].scatter(scaled_speed[:nb_points-1], from_px_to_mm*aggregated_data['MinError'][:nb_points-1], color=colors[pipeline], s=10, alpha=0.5, label=labels[pipeline])  # Legend only here
        lin_reg_params.append([pipeline,'MinError',  linregress(scaled_speed[:nb_points-1], from_px_to_mm*aggregated_data['MinError'][:nb_points-1])])
        if plot_regressor:
            m = lin_reg_params[-1][2].slope
            b = lin_reg_params[-1][2].intercept
            y = [m * xi + b for xi in x]
            axs[2].plot(x, y, color='k', linewidth=1)

    # Draw vertical lines in each subplot
    for ax in axs:
        ax.axvline(x=lim_lm, color='black', linestyle='dotted')  # Vertical line at x = 0.25
        ax.axvline(x=lim_mh, color='black', linestyle='dotted')   # Vertical line at x = 0.6

    text_y_scaler = 0.92
    # Set axis labels and limits for each subplot
    ax_0_lim_y = 30
    axs[0].set_xlabel('Speed [m/s]\na)')
    axs[0].set_ylabel('Pipeline Latency [ms]')
    axs[0].set_xlim(0, plot_x_max)
    axs[0].set_ylim(0, ax_0_lim_y)
    axs[0].text(x_low, ax_0_lim_y*text_y_scaler, 'Low', ha='center', fontsize=f_sz)
    axs[0].text(x_medium, ax_0_lim_y*text_y_scaler, 'Medium', ha='center', fontsize=f_sz)
    axs[0].text(x_high, ax_0_lim_y*text_y_scaler, 'High', ha='center', fontsize=f_sz)
    axs[0].grid(True)  # Enable grid

    ax_1_lim_y = 30
    axs[1].set_xlabel('Speed [m/s]\nb)')
    axs[1].set_xlim(0, plot_x_max)
    axs[1].set_ylabel('Real-Time Offset [mm]')
    axs[1].set_ylim(0, ax_1_lim_y)  # Limiting Y-axis between 0 and 20
    # axs[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    axs[1].text(x_low, ax_1_lim_y*text_y_scaler, 'Low', ha='center', fontsize=f_sz)
    axs[1].text(x_medium, ax_1_lim_y*text_y_scaler, 'Medium', ha='center', fontsize=f_sz)
    axs[1].text(x_high, ax_1_lim_y*text_y_scaler, 'High', ha='center', fontsize=f_sz)
    axs[1].grid(True)  # Enable grid

    ax_2_lim_y = 30
    axs[2].set_xlim(0, plot_x_max)
    axs[2].set_xlabel('Speed [m/s]\nc)')
    axs[2].set_ylabel('Tracking Error [mm]')
    axs[2].set_ylim(0, ax_2_lim_y)  # Limiting Y-axis between 0 and 20
    # axs[2].yaxis.set_major_locator(MaxNLocator(integer=True))
    axs[2].text(x_low, ax_2_lim_y*text_y_scaler, 'Low', ha='center', fontsize=f_sz)
    axs[2].text(x_medium, ax_2_lim_y*text_y_scaler, 'Medium', ha='center', fontsize=f_sz)
    axs[2].text(x_high, ax_2_lim_y*text_y_scaler, 'High', ha='center', fontsize=f_sz)
    axs[2].grid(True)  # Enable grid

    # Move the legend outside the third plot
    axs[0].legend().remove()
    axs[1].legend(ncol=2, loc='upper center', bbox_to_anchor=(0.5, 1.2), fontsize=10)  # Increase fontsize as needed
    axs[2].legend().remove()


    # Show the plots
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.3)  # Adjust the value (e.g., 0.5) for more space between subplots


    for lrp in lin_reg_params:
            print(lrp[0])
            print(f'\t{lrp[1]}:')
            print(f'\t\tm = {lrp[2].slope:.3f}')
            print(f'\t\tb = {lrp[2].intercept:.3f}')
            print(f'\t\tr:= {lrp[2].rvalue:.3f}')
            print(f'\t\tp:= {lrp[2].pvalue:.6f}')


    plt.savefig(f'results/images/summary/{args.type}_metrics_vs_speed.png')
