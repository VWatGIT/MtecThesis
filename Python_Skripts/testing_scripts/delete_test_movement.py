import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

from Python_Skripts.Function_Groups.object3D import Sensor, Hexapod
from Python_Skripts.Function_Groups.path_creation import generate_snake_path, generate_grid


if __name__ == "__main__":
    # Set up Measurement Grid
    grid_size = [2, 2, 2]  # [mm]
    step_size = 2  # [mm]
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
    


    # Set up the Sensor
    sensor = Sensor()
    hexapod = Hexapod()

    """
    # Move the Hexapod along the snake path
    hexapod.move_to_default_position()

    # Move the Hexapod near the probe tip
    #probe_tip_position = detect_probe_tip_position() # TODO: implement this function
    probe_tip_position = [0, 0, 0, 0, 0, 0]  # [x, y, z]
    sensor_position = sensor.position # TODO: account for both position and rotation

    relative_posiiton = [probe_tip_position[i] - sensor_position[i] for i in range(6)] 

    hexapod.move(relative_posiiton, flag = "relative") # TODO set the correct position with room to spare
    """
    
    absolute_signal_positions = []

    for i in range(0, len(path_x_snake)):
        # Move the Hexapod to the next position
        #hexapod.move([path_x_snake[i], path_y_snake[i], path_z_snake[i], 0, 0, 0], flag = "relative")

        # Get the sensor signal
        #signal = sensor.get_signal()
        signal = sensor.get_test_signal()

        # add the signal postion to the measurement point position
        relative_signal_position = (signal.xpos, signal.ypos)
        absolute_signal_position = [path_x_snake[i] + relative_signal_position[0], path_y_snake[i], path_z_snake[i]+ relative_signal_position[1]] 
        # TODO merge coordinate systems correctly (Sensor x --> path x, Sensor y --> path z, Sensor z --> path y) 
        absolute_signal_positions.append(absolute_signal_position)

        # TODO: write function to use signal.sum to determine beam dimensions
        
        print(f"Measurement Point: {i}")
        print(f"Snake Path Position: {path_x_snake[i], path_y_snake[i], path_z_snake[i]}")
        print(f"relative Signal Position: {relative_signal_position}")
        print(f"absolute Signal Position: {absolute_signal_position}")

        # update plot
        ax.scatter(X_flat, Y_flat, Z_flat, c='blue', marker='o', label='Grid Points')
        ax.plot(path_x_snake[:i+1], path_y_snake[:i+1], path_z_snake[:i+1], c='red', label='Snake Path') # +1 to include the last point
        ax.scatter(absolute_signal_position[0], absolute_signal_position[1], absolute_signal_position[2], c='green', marker='o', label='Signal Position') 
        
        plt.pause(0.1)

    

    plt.show()





    