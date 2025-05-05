import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pdb


# Read the CSV file
filename = 'results/syn_summary_ok.csv'  # Updated with the correct file path
df = pd.read_csv(filename)

# Extract speed category from the 'Recording' column
df['Speed'] = df['Recording'].str.extract(r'Synthetic_(high|medium|low)_')[0]

# Define plot settings
categories = ['high', 'medium', 'low']
colors = {'spinnaker': '#006666', 'gpu': '#4C0099'}
# Create subplots
fig, ax = plt.subplots(1, 1, figsize=(4, 4), sharey=True)
fig.suptitle('Latency vs Error and MinError')

m = []
b = []
r = []
pl = [] # pipeline latency
ro = [] # RT offset
te = [] # Tracked-Position error

for pipeline in ['spinnaker','gpu']:
    pipeline_data = df[df['Pipeline'] == pipeline]
    l_mean = pipeline_data['Latency'].mean()
    l_std = pipeline_data['Latency'].std()
    o_mean = pipeline_data['Error'].mean()
    o_std = pipeline_data['Error'].std()
    e_mean = pipeline_data['MinError'].mean()
    e_std = pipeline_data['MinError'].std()
    pl.append((l_mean, l_std))
    ro.append((o_mean, o_std))
    te.append((e_mean, e_std))
    if not pipeline_data.empty:
        # Latency vs Error
        ax.scatter(pipeline_data['MaxSpeed'], pipeline_data['Error'], 
                    label=f"{pipeline.capitalize()}", color=colors[pipeline], alpha=0.6) 
        slope, intercept, r_value, p_value, std_err = linregress(pipeline_data['MaxSpeed'], pipeline_data['Error'])
        m.append(slope)
        b.append(intercept)
        r.append(r_value)
        print(f'For {pipeline}')
        print(f"\t Latency: {l_mean:.2f} ± {l_std:.2f} ms")
        print(f"\t RT Offset: {o_mean:.2f} ± {o_std:.2f} ms")
        print(f"\t Tracked P. Error: {e_mean:.2f} ± {e_std:.2f} ms")
        print(f"\t Slope: {slope:.1f}mm/ms")
        print(f"\t Intercept: {intercept:.3f}mm")
        print(f"\t r_value: {r_value:.3f}")

    ax.set_xlabel('Speed')
    ax.legend()
    ax.grid(True)

# Set shared y-axis label
ax.set_ylabel('Real-Time Offset')

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.95])

# Show the plot
plt.savefig('results/images/summary/speed_vs_rt_offset.png')

# Compute x-coordinate of intersection
x_intersect = (b[1] - b[0]) / (m[0] - m[1])

# Compute y-coordinate of intersection
y_intersect = m[1] * x_intersect + b[1]

print(f"Intersection point: x = {x_intersect}, y = {y_intersect}")
print(f"Slope ratio (GPU/SPK): {m[1]/m[0]:.3f}")
print(f"Latency ratio (GPU/SPK): {pl[1][0]/pl[0][0]:.3f}")
