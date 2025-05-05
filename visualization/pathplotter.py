import numpy as np
import pdb
import h5py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import argparse
import os
import re
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
from matplotlib.colors import LinearSegmentedColormap


def file_exists(directory, filename):
    # Construct the full file path
    file_path = os.path.join(directory, filename)
    
    # Check if the file exists
    return os.path.isfile(file_path)

def list_path_numbers(directory):
    # Regular expression to match files named path_<number>.h5
    pattern = re.compile(r'^path_(\d+)\.h5$')
    
    # List to hold the extracted numbers
    numbers = []
    
    # Get a list of all files in the directory
    files = os.listdir(directory)
    
    # Iterate over the files and extract the numbers
    for file in files:
        match = pattern.match(file)
        if match:
            numbers.append(int(match.group(1)))
    
    return numbers

def create_point_cloud_from_frames(cloud):
    width, height, depth = cloud.shape

    # Create an empty list to store points
    points = []
    max_duration = 3000

    for z in range(depth):
        if z > max_duration:
            break
        frame = cloud[:,:,z]
        for y in range(height):
            for x in range(width):
                intensity = frame[x,y]
                if intensity > 0:  # Consider only non-zero intensity pixels
                    points.append([x, y, z])

    points = np.array(points)
    return points

def plot_histogram_with_gaussians(data, num_bins=30, save_path="histogram_with_gaussians.png"):
    
    # Fit a Gaussian Mixture Model with two components
    gmm = GaussianMixture(n_components=2)
    data = data.reshape(-1, 1)  # Reshape for GMM (expects 2D array)
    gmm.fit(data)
    
    # Get the parameters of the two Gaussians (means, variances)
    means = gmm.means_.flatten()
    variances = gmm.covariances_.flatten()
    
    # Sort the means and variances so the narrower one comes first
    sorted_indices = np.argsort(variances)
    mean_1, mean_2 = means[sorted_indices]
    variance_1, variance_2 = variances[sorted_indices]
    
    # Find the center of the narrower distribution
    narrower_mean = mean_1
    print(f"Centers of the Gaussians: {mean_1}, {mean_2}")
    print(f"Narrower distribution's mean: {narrower_mean}")
    
    # Plot the histogram of the data
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=num_bins, density=True, alpha=0.6, color='g', label='Data Histogram')
    
    # Plot the Gaussian fit lines
    x = np.linspace(min(data), max(data), 1000).reshape(-1, 1)
    y1 = norm.pdf(x.flatten(), mean_1, np.sqrt(variance_1))
    y2 = norm.pdf(x.flatten(), mean_2, np.sqrt(variance_2))
    
    plt.plot(x, y1, label=f'Gaussian 1 (mean={mean_1:.2f}, var={variance_1:.2f})', color='blue')
    plt.plot(x, y2, label=f'Gaussian 2 (mean={mean_2:.2f}, var={variance_2:.2f})', color='red')
    
    # Add labels and title
    plt.xlabel('Data Values')
    plt.ylabel('Density')
    plt.title('Histogram with Gaussian Fits')
    
    # Highlight the center of the narrower distribution
    plt.axvline(x=narrower_mean, color='purple', linestyle='--', label=f'Narrower Gaussian Center ({narrower_mean:.2f})')
    
    # Show legend
    plt.legend()
    
    # Save the plot with transparent background
    plt.savefig(save_path, dpi=1200, bbox_inches='tight')

    plt.close()

    return narrower_mean
    

def display_point_cloud(points, nb_frames, fname, mode):
    
    


    keep_looking = True
    frames_missing = 5
    pt_ix = points.shape[0]-1
    frame_ix = points[pt_ix,2]
    while keep_looking:
        if frame_ix > points[pt_ix,2]:
            frames_missing -= 1
            frame_ix = points[pt_ix,2]
            if frames_missing == 0:
                keep_looking = False            
        pt_ix -= 1

    if mode == 'Synthetic':
        mean_x = np.mean(points[pt_ix:-1, 0]) 
        mean_y = np.mean(points[pt_ix:-1, 1]) 
        cbar_orientation='horizontal'
    else:
        mean_x = plot_histogram_with_gaussians(points[pt_ix:-1, 0], save_path=f'images/{fname}_x.png')
        mean_y = plot_histogram_with_gaussians(points[pt_ix:-1, 1], save_path=f'images/{fname}_y.png')
        cbar_orientation='vertical'
                 

    square_length = 33

    plt.figure(figsize=(6,6))
    plt.scatter(points[pt_ix:-1, 0], points[pt_ix:-1, 1], color="#029145", marker='o', s=100)
    plt.xlim(mean_x-square_length/2, mean_x+square_length/2)
    plt.ylim(mean_y-square_length/2, mean_y+square_length/2)
    plt.xticks([])  # Remove x-axis ticks
    plt.yticks([])  # Remove y-axis ticks
    plt.savefig(f'images/{fname}_2D.png')
    plt.close()

    # Define max_x and max_y based on your data
    max_t = points[:, 2].max()
    max_x = points[:, 0].max()
    max_y = points[:, 1].max()

    min_t = 0
    min_x = 0
    min_y = 0

    soft_edge_color = '#DCDCDC'
    hard_edge_color = '#DCDCDC'

    edge_width = 0.5

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot([min_t, max_t], [max_x, max_x], [max_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle=':')
    ax.plot([max_t, max_t], [min_x, max_x], [max_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle=':') 
    ax.plot([max_t, max_t], [max_x, max_x], [min_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle=':') 

    ax.plot([min_t, max_t], [min_x, min_x], [max_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle='-')
    ax.plot([max_t, max_t], [min_x, min_x], [min_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle='-') 
    ax.plot([min_t, min_t], [min_x, max_x], [max_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle='-') 
    ax.plot([max_t, max_t], [min_x, max_x], [min_y, min_y], color=soft_edge_color, linewidth=edge_width, linestyle='-') 

    ax.plot([min_t, max_t], [max_x, max_x], [min_y, min_y], color=soft_edge_color, linewidth=edge_width, linestyle='-')
    ax.plot([min_t, min_t], [max_x, max_x], [min_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle='-')

    # ax.plot([min_t, min_t], [min_x, min_x], [min_y, max_y], color=soft_edge_color, linewidth=edge_width, linestyle='-')  
    # ax.plot([min_t, max_t], [min_x, min_x], [min_y, min_y], color=soft_edge_color, linewidth=edge_width, linestyle='-') 
    # ax.plot([min_t, min_t], [min_x, max_x], [min_y, min_y], color=soft_edge_color, linewidth=edge_width, linestyle='-') 

    green_map = LinearSegmentedColormap.from_list("white_to_green", ["#FFFFFF", "#00B050"])
    grey_map = LinearSegmentedColormap.from_list("white_to_grey", ["#FFFFFF", "#DCDCDC"])
    colors = points[0:pt_ix, 2]  # Use the z-coordinate as the color values
    
    # Grey projections
    # ax.scatter(points[0:pt_ix, 2], points[0:pt_ix, 0], points[0:pt_ix, 1]*0,  c=colors, cmap=grey_map, marker='.', s=0.02, alpha=0.02)
    # ax.scatter(points[0:pt_ix, 2], points[0:pt_ix, 0]*0, points[0:pt_ix, 1],  c=colors, cmap=grey_map, marker='.', s=0.02, alpha=0.02)
    
    # Green XY events over time
    ev_xyt = ax.scatter(points[0:pt_ix, 2], points[0:pt_ix, 0], points[0:pt_ix, 1],  c=colors, cmap=green_map, marker='.', s=0.1, alpha=0.5)
    
    ax.scatter(points[pt_ix:-1, 2], points[pt_ix:-1, 0], points[pt_ix:-1, 1], color="#029145", marker='.', s=0.5)
                     

    shall_draw_square = False
    if shall_draw_square:
        half_length = square_length / 2

        # Define the square's corners in the YZ plane at X = max_x
        square_corners = [
            (max_t, mean_x - half_length, mean_y - half_length),  # Bottom-left
            (max_t, mean_x - half_length, mean_y + half_length),  # Bottom-right
            (max_t, mean_x + half_length, mean_y + half_length),  # Top-right
            (max_t, mean_x + half_length, mean_y - half_length)   # Top-left
        ]

        x_corners, y_corners, z_corners = zip(*square_corners)

        # Close the square (back to the first point)
        x_corners += (x_corners[0],)
        y_corners += (y_corners[0],)
        z_corners += (z_corners[0],)

        ax.plot(x_corners, y_corners, z_corners, color=hard_edge_color, linestyle=':')


    ax.set_xlim(0, nb_frames) # Z
    ax.set_ylim(0, 256) # X
    ax.set_zlim(0, 165) # Y

    # Hide ticks on X and Z axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    
    r1 = round(1,2)
    r2 = round(256/165,2)
    r3 = round(165/165,2)

    # Set equal aspect ratio
    ax.set_box_aspect([r1, r2, r3])

    ax.set_xlabel('Time')
    ax.set_ylabel('X')
    ax.set_zlabel('Y')
       
    ax.view_init(elev=15, azim=15)    
    ax.grid(False)

    ax.set_axis_off()
 
    
    cbar = plt.colorbar(ev_xyt, ax=ax, shrink=0.5, orientation=cbar_orientation)
    cbar.set_label('Time [ms]')  # Label for the color bar
    cbar.set_ticks([0, 1000, 2000, 3000])  # Set specific ticks


    # Adjust subplot parameters to reduce margins
    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)

    plt.savefig(f"images/{fname}_3D.png", dpi=1200, transparent=True, bbox_inches='tight')

    plt.close()



def parse_args():

    parser = argparse.ArgumentParser(description='Frame Saver')

    parser.add_argument('-p', '--path', type= int, help="Path to  plot", default=-1)
    parser.add_argument('-m', '--mode', type= str, help="Synthetic|Recording", default='Synthetic')

    return parser.parse_args()

if __name__ == '__main__':
    
    args = parse_args()
    mode = args.mode

    if args.path == -1:
        nb_list = list_path_numbers("paths")
    else:
        nb_list = [args.path]

    for suffix in nb_list:
        print(suffix)

        fname = f"path_{suffix}"

        if file_exists("images", f"{fname}_front.png"):
            print(f"Image for {fname} already exists")
            continue
        else:
            print(f"Creating image for {fname}")
            # Load the array from the HDF5 file
            with h5py.File(f'paths/{fname}.h5', 'r') as f:
                cloud = f['cloud'][:]


            nb_frames = cloud.shape[2]


            # Create point cloud
            points = create_point_cloud_from_frames(cloud)

            # Display point cloud
            display_point_cloud(points, nb_frames, fname, mode)
