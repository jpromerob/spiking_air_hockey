import numpy as np

import warnings
warnings.filterwarnings("ignore", message="Unable to import Axes3D")
import matplotlib.pyplot as plt


HIGH_DPI = 200

# Load the .npz file
for accelerator in ['gpu', 'spinnaker']:
    for i in range(10):
        loaded = np.load(f'Synthetic_241013_003303_v{i+1}_{accelerator}_t_shift_vs_error.npz')
        # loaded = np.load(f'Synthetic_241013_001233_v{i+1}_gpu_t_shift_vs_error.npz')

        t_shift = loaded['t_shift']
        error = loaded['error']

        # min_error_index = np.argmin(error)

        # plt.scatter(t_shift, error, color='k', s=4)
        plt.scatter(t_shift, error, s=4)
        # plt.scatter(t_shift[min_error_index], error[min_error_index], marker='x', color='r', s=100)
        # plt.text(t_shift[min_error_index], error[min_error_index]*0.6, f"Latency = {t_shift[min_error_index]} [ms]", fontsize=12, color='red', bbox=dict(facecolor='white', alpha=0.5))


    plt.title(f'@{accelerator} ... Finding Latency: Time Shift vs Error')
    plt.xlabel('Time Shift in [ms]')
    plt.ylabel('Error inn [mm]')

    # Setting limits
    plt.xlim(0, 40)
    plt.ylim(0, 10)

    # plt.tight_layout()

    plt.savefig(f'trash_{accelerator}.png', format='png', dpi=HIGH_DPI)
    plt.clf()
