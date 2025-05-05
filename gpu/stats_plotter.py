import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the CSV file
data = pd.read_csv('results/data/stats.csv')

# Create a figure and a scatter plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot the first scatter plot with the first X axis
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylabel('GPU Utilization (%)', color='black')


ax1.scatter(data['nb_neurons'], data['gpu'], color='green', alpha=0.7)  # Replace 'other_mem' and 'other_metric' with your actual column names
ax1.set_xlabel('\n# Neurons Instantiated', color='green')
ax1.tick_params(axis='x', labelcolor='green')

# Create a second X axis sharing the same Y axis
ax2 = ax1.twiny()

ax2.scatter(data['mem'], data['gpu'], color='red', alpha=0.7)
ax2.set_xlabel('Memory [MB]\n', color='red')
ax2.tick_params(axis='x', labelcolor='red')


# Adding titles and grid
ax1.grid(True)

# Display the plot
plt.savefig('results/images/stats.png')
plt.clf()


# Create a figure and a scatter plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# Plot the first scatter plot with the first X axis
ax1.tick_params(axis='y', labelcolor='black')
ax1.set_ylabel('Memory [MB]', color='black')


ax1.scatter(data['nb_neurons'], data['mem'], color='blue', alpha=0.7)  # Replace 'other_mem' and 'other_metric' with your actual column names
ax1.set_xlabel('\n# Neurons Instantiated', color='black')
ax1.tick_params(axis='x', labelcolor='black')

# Adding titles and grid
ax1.grid(True)

# Display the plot
plt.savefig('results/images/stats_nn_mem.png')
plt.clf()