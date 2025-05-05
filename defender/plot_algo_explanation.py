import matplotlib.pyplot as plt
import numpy as np
import argparse
from matplotlib.colors import LinearSegmentedColormap

# Create custom colormaps
cmap_red = LinearSegmentedColormap.from_list('custom_white_red', ['white', '#FF0000'])
cmap_orange = LinearSegmentedColormap.from_list('custom_white_orange', ['white', '#FF8C00'])

def parse_args():
    parser = argparse.ArgumentParser(description='Defense Trajectory Example')
    parser.add_argument('-f', '--filename', type=str, help="Filename", default="")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()

    # Load the trajectory data
    trajectory = np.load(f'{args.filename}')
    t = trajectory['t']
    puck_x = trajectory['puck_x']
    puck_y = trajectory['puck_y']

    max_x = 10
    min_x = - max_x
    max_y = 64
    half_y = 20
    middle_line = max_y - half_y
    min_y = max_y - 2 * half_y
    base_right = 28
    mirror_line = int((middle_line + base_right) * 0.5)

    paddle_x = np.zeros(puck_x.shape)
    paddle_y = np.zeros(puck_y.shape)

    # Behavior of Paddle_X
    for i in range(len(paddle_x)):
        if puck_y[i] > middle_line:
            paddle_x[i] = (max_y - puck_y[i]) / half_y * puck_x[i]
        elif puck_y[i] < mirror_line:
            paddle_x[i] = 0
        else:
            paddle_x[i] = puck_x[i]

    # Behavior of Paddle_Y
    for i in range(len(paddle_y)):
        if puck_y[i] >= middle_line:
            paddle_y[i] = min_y + (base_right - min_y) * (max_y - puck_y[i]) / half_y
        elif puck_y[i] < mirror_line:
            paddle_y[i] = min_y
        else:
            paddle_y[i] = mirror_line - abs(puck_y[i] - mirror_line)

    # Create a single plot
    fig, ax = plt.subplots(figsize=(8, 4), dpi=400)

    offset = 10


    # Scatter plot for the puck
    sc_puck = ax.scatter(-puck_y[:-offset], puck_x[:-offset], c=t[:-offset], cmap=cmap_red, marker='o', label='Puck')

    # Scatter plot for the paddle
    sc_paddle = ax.scatter(-paddle_y[:-offset], paddle_x[:-offset], c=t[:-offset], cmap=cmap_orange, marker='o', label='Paddle')

    s_clash = ax.scatter(-puck_y[-1], puck_x[-1], color='black', marker='x', s=100)

    # Add axis labels, title, and customize axis limits
    ax.set_title(' ')
    ax.set_xlabel('← y')
    ax.set_ylabel('x →')
    ax.set_ylim(min_x - 0.5, max_x + 0.5)
    ax.set_xlim(-(max_y), -(min_y))

    # Remove ticks from both x and y axes
    ax.set_xticks([])
    ax.set_yticks([])

    # Add vertical lines and text
    ax.axvline(x=-middle_line, color='black', linestyle=':')
    ax.axvline(x=-mirror_line, color='black', linestyle='--')
    ax.axvline(x=-base_right, color='black', linestyle=':')
    ax.text(0.69, 1.04, '⬐ Defense Line', transform=ax.transAxes)
    ax.text(0.31, 1.04, 'Middle Line ⬎', transform=ax.transAxes)
    ax.text(0.73, -0.10, 'Mirroring\n Region', transform=ax.transAxes)

    # Add colorbar for the paddle on the right
    cbar_paddle = fig.colorbar(sc_paddle, ax=ax, location='right')
    cbar_paddle.set_label('time [ms]')

    # Add colorbar for the puck on the left
    cbar_puck = fig.colorbar(sc_puck, ax=ax, location='right')
    cbar_puck.ax.tick_params(labelsize=0, length=0)



    # Save the plot
    base_name = args.filename.rsplit('.', 1)[0]
    plt.tight_layout()
    plt.savefig(f"{base_name.replace('data', 'images', 1)}_combined_control_summary.png")
