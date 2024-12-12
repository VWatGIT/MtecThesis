import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

def generate_snake_path(X, Y, Z): # switch
    path_points = []
    x_dim, y_dim, z_dim = X.shape
    
    # Path first goes to
    # 1. Z direction
    # 2. Y direction
    # 3. X direction


    for y in range(y_dim):
        if y % 2 == 0:  # Even layers
            for x in range(x_dim):
                if x % 2 == 0:  # Even rows
                    for z in range(z_dim):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
                else:  # Odd rows
                    for z in range(z_dim-1, -1, -1):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
        else:  # Odd layers
            for x in range(x_dim-1, -1, -1):
                if x % 2 == 0:  # Even rows
                    for z in range(z_dim-1, -1, -1):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])
                else:  # Odd rows
                    for z in range(z_dim):
                        path_points.append([X[x, y, z], Y[x, y, z], Z[x, y, z]])

    return np.array(path_points)

def generate_grid(grid_size, step_size):
    # All coordinates with respect to the Hexapod Coordinate System
    y = np.linspace(-grid_size[0]/2, grid_size[0]/2, int(grid_size[0] / step_size)+1) # +1 for off by 1 error due to 0 - size grid
    z = np.linspace(-grid_size[1]/2, grid_size[1]/2, int(grid_size[1] / step_size)+1)
    x = np.linspace(0, -grid_size[2], int(grid_size[2] / step_size)+1) 

    X, Y, Z = np.meshgrid(x, y, z)
    
    return X, Y, Z 

if __name__ == "__main__":
    # Set up Measurement Grid
    grid_size = [2, 2, 2]  # [mm]
    step_size = 1 # [mm]
    X, Y, Z = generate_grid(grid_size, step_size)

    # Generate the snake path
    path_points_snake = generate_snake_path(X, Y, Z)
    #print(path_points_snake)

    # Extract the path coordinates
    path_x_snake = path_points_snake[:, 0]
    path_y_snake = path_points_snake[:, 1] # TODO switch ?
    path_z_snake = path_points_snake[:, 2]

    # Visualize the grid and the snake path
    # Create a 3D plot for the snake path
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the meshgrid points
    X_flat = X.flatten()
    Y_flat = Y.flatten()
    Z_flat = Z.flatten()

    ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points', s = 5)

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
        #plt.pause(0.1)  # Pause to update the plot

    # Simulate the movement of the hexapod
    for i in range(1, len(path_points_snake) + 1):
        update_path_plot(i)
        #time.sleep(0.2)  # Simulate time delay for movement

    plt.show()

    # Extract planes where x equals a specific value
    x_value = path_points_snake[0, 0]
    print("x_value:", x_value)

    x_index = np.where(X[:, 0, 0] == x_value)  # Find the index of the specific x value 
    print("x_index:", x_index)

    X_plane = X[x_index]
    Y_plane = Y[x_index]
    Z_plane = Z[x_index]

    print("X_plane:", X_plane)
    print("Y_plane:", Y_plane)
    print("Z_plane:", Z_plane)
        

    # Plot the plane
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points', s = 5)
    ax.plot_surface(X_plane, Y_plane, Z_plane, color='blue', alpha=0.3, rstride=100, cstride=100)
    
    plt.show()

    
