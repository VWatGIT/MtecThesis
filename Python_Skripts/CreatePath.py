import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

def generate_snake_path(X, Y, Z): 
    # step size = [x,y,z] = [0.001, 1, 1]
    path_points = []
    x_dim, y_dim, z_dim = X.shape
    
    dim_index = [0, 1, 2] # x, y, z
    dim_values = [x_dim, y_dim, z_dim]
    

    # Sort dimensions based on number of path_points
    sorted_dims = sorted(zip(dim_values, dim_index), reverse=True)
    ordered_dim_values = [dim_value for dim_value, _ in sorted_dims]
    ordered_dim_index = [dim for _, dim in sorted_dims]
   
    # Path should go to the axis with most points first to improve efficiency
    first_dim = ordered_dim_values[0]
    second_dim = ordered_dim_values[1]
    last_dim = ordered_dim_values[2]

    for last in range(last_dim):
        if last % 2 == 0:  # Even layers
            for second in range(second_dim):
                if second % 2 == 0:  # Even rows
                    for first in range(first_dim):
                        coords = [0, 0, 0]
                        coords[ordered_dim_index[0]] = first
                        coords[ordered_dim_index[1]] = second
                        coords[ordered_dim_index[2]] = last
                        path_points.append([X[coords[0], coords[1], coords[2]], 
                                            Y[coords[0], coords[1], coords[2]], 
                                            Z[coords[0], coords[1], coords[2]]])
                else:  # Odd rows
                    for first in range(first_dim-1, -1, -1):
                        coords = [0, 0, 0]
                        coords[ordered_dim_index[0]] = first
                        coords[ordered_dim_index[1]] = second
                        coords[ordered_dim_index[2]] = last
                        path_points.append([X[coords[0], coords[1], coords[2]], 
                                            Y[coords[0], coords[1], coords[2]], 
                                            Z[coords[0], coords[1], coords[2]]])
        else:  # Odd layers
            for second in range(second_dim-1, -1, -1):
                if second % 2 == 0:  # Even rows
                    for first in range(first_dim-1, -1, -1):
                        coords = [0, 0, 0]
                        coords[ordered_dim_index[0]] = first
                        coords[ordered_dim_index[1]] = second
                        coords[ordered_dim_index[2]] = last
                        path_points.append([X[coords[0], coords[1], coords[2]], 
                                            Y[coords[0], coords[1], coords[2]], 
                                            Z[coords[0], coords[1], coords[2]]])
                else:  # Odd rows
                    for first in range(first_dim):
                        coords = [0, 0, 0]
                        coords[ordered_dim_index[0]] = first
                        coords[ordered_dim_index[1]] = second
                        coords[ordered_dim_index[2]] = last
                        path_points.append([X[coords[0], coords[1], coords[2]], 
                                            Y[coords[0], coords[1], coords[2]], 
                                            Z[coords[0], coords[1], coords[2]]])
   
    return np.array(path_points)

def generate_grid(grid_size, step_size):
    # step_size = [x,y,z]
    # grid_size = [x,y,z]
    # All coordinates with respect to the Hexapod Coordinate System

    x = np.linspace(0, -grid_size[0], int(grid_size[0] / step_size[0])+1) 
    y = np.linspace(-grid_size[1]/2, grid_size[1]/2, int(grid_size[1] / step_size[1])+1) # +1 for off by 1 error due to 0 - size grid
    z = np.linspace(-grid_size[2]/2, grid_size[2]/2, int(grid_size[2] / step_size[2])+1)
    

    X, Y, Z = np.meshgrid(x, y, z)
    
    return X, Y, Z 

if __name__ == "__main__":
    # Set up Measurement Grid
    grid_size = [1, 1, 1]  # [mm]
    step_size = [0.5,0.2,0.3] # [mm]
    X, Y, Z = generate_grid(grid_size, step_size)
    print(X.shape, Y.shape, Z.shape)

    # Generate the snake path
    path_points_snake = generate_snake_path(X, Y, Z)
    print(path_points_snake)

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
    #print("x_value:", x_value)

    x_index = np.where(X[:, 0, 0] == x_value)  # Find the index of the specific x value 
    #print("x_index:", x_index)

    X_plane = X[x_index]
    Y_plane = Y[x_index]
    Z_plane = Z[x_index]

    #print("X_plane:", X_plane)
    #print("Y_plane:", Y_plane)
    #print("Z_plane:", Z_plane)
        

    # Plot the plane
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points', s = 5)
    ax.plot_surface(X_plane, Y_plane, Z_plane, color='blue', alpha=0.3, rstride=100, cstride=100)
    
    plt.show()

    
