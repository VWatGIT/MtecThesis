import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

def generate_snake_path(X, Y, Z):
    path_points = []
    x_dim, y_dim, z_dim = X.shape

    for z in range(z_dim):
        if z % 2 == 0:  # Even layers
            for y in range(y_dim):
                if y % 2 == 0:  # Even rows
                    for x in range(x_dim):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
                else:  # Odd rows
                    for x in range(x_dim-1, -1, -1):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
        else:  # Odd layers
            for y in range(y_dim-1, -1, -1):
                if y % 2 == 0:  # Even rows
                    for x in range(x_dim-1, -1, -1):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
                else:  # Odd rows
                    for x in range(x_dim):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])

    return np.array(path_points)

def generate_grid(grid_size, step_size):
    x = np.linspace(0, grid_size[0], int(grid_size[0] / step_size)+1) # +1 for off by 1 error due to 0 - size grid
    y = np.linspace(0, grid_size[1], int(grid_size[1] / step_size)+1)
    z = np.linspace(0, grid_size[2], int(grid_size[2] / step_size)+1)
    X, Y, Z = np.meshgrid(x, y, z)


    return X, Y, Z

"""
# Set up Measurement Grid
grid_size = [2, 2, 4]  # [mm]
step_size = 1  # [mm]
X, Y, Z = generate_grid(grid_size, step_size)

# Generate the snake path
path_points_snake = generate_snake_path(X, Y, Z)

# Extract the path coordinates
path_x_snake = path_points_snake[:, 0]
path_y_snake = path_points_snake[:, 1]
path_z_snake = path_points_snake[:, 2]

# Visualize the grid and the snake path
# Create a 3D plot for the snake path
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the meshgrid points
X_flat = X.flatten()
Y_flat = Y.flatten()
Z_flat = Z.flatten()

ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points')

# Initialize the path plot
path_plot, = ax.plot([], [], [], color='red', marker='o', label='Hexapod Path')

# Set plot labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Meshgrid with Hexapod Path')
ax.legend()

# Function to update the path plot
def update_path_plot(current_index):
    path_plot.set_data(path_x_snake[:current_index], path_y_snake[:current_index])
    path_plot.set_3d_properties(path_z_snake[:current_index])
    plt.draw()
    plt.pause(0.1)  # Pause to update the plot

# Simulate the movement of the hexapod
for i in range(1, len(path_points_snake) + 1):
    update_path_plot(i)
    #time.sleep(0.2)  # Simulate time delay for movement

plt.show()
"""