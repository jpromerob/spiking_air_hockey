import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap
import argparse
import pdb

# Define the colors from black to yellow to red
colors = ["black", "yellow", "red"]

# Create the custom colormap
custom_cmap = LinearSegmentedColormap.from_list("black_yellow_red", colors, N=256)


def parse_args():

    parser = argparse.ArgumentParser(description='Automatic Coordinate Location')

    parser.add_argument('-n', '--net', type=str, help="Net name: convolutioner|mapper|projector", default="convolutioner")

    return parser.parse_args()

if __name__ == '__main__':

    args = parse_args()

    
    net = args.net

    index_empty = 24

    print(f'\nData for {net}')

    if net == 'convolutioner':
        app_label = 'cnn'
    else:
        app_label = 'output'
    
    # Load CSV data into a DataFrame
    df = pd.read_csv(f'results/data/parsed_{net}.csv', delimiter=',')

    # pdb.set_trace()
    print(f"Non-System cores: {df[~df['vertex'].str.contains('SYSTEM', case=False, na=False)].shape[0]}")

    for pattern in ['SYSTEM', 'command', app_label]:  
        if pattern in ['cnn','output']:
            pattern_label = 'Application'
        else:
            pattern_label = pattern
        print(f"{pattern_label.capitalize()} cores: {df[df['vertex'].str.contains(pattern, case=False, na=False)].shape[0]}")

    print(f"System uses {df[~df['vertex'].str.contains(app_label, case=False, na=False)]['SDRAM'].sum()/1024/1024:.3f} MB of SDRAM")
    print(f"Application uses {df[df['vertex'].str.contains(app_label, case=False, na=False)]['SDRAM'].sum()/1024/1024:.3f} MB of SDRAM")


    # Initialize the loader array with zeros (49 x 25)
    loader = np.zeros((49, 25))
    # Populate the loader array with memory usage values from the DataFrame
    for _, row in df.iterrows():
        processor_id = int(row['processor_id'])
        chip_id = int(row['chip_id'])
        board_id = int(row['board_id'])
        mem_used = int(row['SDRAM'])/1024/1024
        if board_id < index_empty:
            loader[chip_id, board_id] += mem_used
        else:
            loader[chip_id, board_id+1] += mem_used



    plotter = np.zeros((35,35))

    import pdb
    idx = -1
    for i in range (5):
        for j in range(5):
            
            idx+=1
            chip = loader[:,idx].reshape(7, 7)

            plotter[i*7:i*7+7,j*7:j*7+7] = np.rot90(chip)


    # Plotting the heatmap
    plt.figure(figsize=(10, 8))
    # plt.imshow(plotter,cmap=custom_cmap, interpolation='nearest', vmin=0, vmax=1.2)
    plt.imshow(plotter,cmap=custom_cmap, interpolation='nearest')
    plt.colorbar(label='Memory Used [MB]')
    plt.title('Memory Usage per Chip\n 48 chips per SpiNN-5 board\n24 SpiNN-5 Boards in System')
    plt.xticks([])
    plt.yticks([])


    # Add a white square overlay at the specified position
    ax = plt.gca()
    square_size = 7
    print(int(index_empty/5))
    print(index_empty%5)
    square_position = ((index_empty%5)*7-0.5, int(index_empty/5)*7-0.5)
    # square_position = (7*2-0.5, 7*2-0.5)  # Example position (x, y)
    rect = Rectangle(square_position, square_size, square_size, linewidth=2, edgecolor='white', facecolor='white')
    ax.add_patch(rect)

    idx = -1
    for j in range(5):
        for i in range (5):
            idx+=1
            if idx < index_empty:
                board_id = f'{idx}'
            elif idx == index_empty:
                board_id = ''
            else:
                board_id = f'{idx-1}'
            square_size = 1
            square_position = (i*7+6-0.5, j*7-0.5)  # Example position (x, y)
            rect = Rectangle(square_position, square_size, square_size, linewidth=0, edgecolor=None, facecolor='white')
            ax.add_patch(rect)
            # Add text at the center of the square
            text_position = (square_position[0] + square_size / 2, square_position[1] + square_size / 2 + 0.1)
            ax.text(text_position[0], text_position[1], board_id, color='black', ha='center', va='center')


    # Add grid lines every 7 ticks
    plt.gca().set_xticks(np.arange(-0.5, 35, 7), minor=True)
    plt.gca().set_yticks(np.arange(-0.5, 35, 7), minor=True)
    plt.gca().grid(which='minor', color='white', linestyle='-', linewidth=1)

    plt.savefig(f'results/images/spinn_mem_{net}.png')
    plt.clf()
    plt.close()
