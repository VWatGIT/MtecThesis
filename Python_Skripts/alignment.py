from Object3D import Sensor, Hexapod
import numpy as np
import matplotlib.pyplot as plt
from CreatePath import generate_snake_path
from data_handling import load_data
import matplotlib.pyplot as plt

# REWORK Functions:

def find_beam_centers(sensor, hexapod, spacing = 1, num_centers = 2, test_slices = None):
    #TODO fix x coordinate of center in testing
    #TODO implement angle calculation


    def grid_search(initial_point, grid_size, step_size):
        max_value = -np.inf
        max_point = None
        path_points_list = [] # testing visualization

        step_size = (step_size, step_size, step_size)

        path_points, grid = generate_snake_path(grid_size, step_size)
        #print(f'Path Points: \n {path_points}')
        last_point = initial_point
        hexapod.move(initial_point, flag = "absolute")
        for i in range(len(path_points)):

            # As Path points are absolute, transform them to relative positions
            next_point = np.array((path_points[i][0], path_points[i][1], path_points[i][2], 0, 0, 0))+np.array((initial_point[0], initial_point[1], initial_point[2], 0 , 0, 0)) 
            next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
            hexapod.move(next_relative_position, flag = "relative")
            last_point = next_point

            signal = sensor.get_signal()
            value = signal.sum

            if test_slice is not None:
                # simulate sensor signal
                # find nearest point in test_slice
                hexapod.position = next_point
                test_points = test_slice["points"][:, :3]
                #test_points[:, 0] = 0

                for i, point in enumerate(test_points):
                    if np.allclose(point[1:], next_point[1:3], atol=step_size[1]/2):
                        value = test_slice["sum_values"][i]
                    else:
                        value = 0

                    if value > max_value:
                        max_value = value
                        x = hexapod.position[0]
                        y = hexapod.position[1]
                        z = hexapod.position[2]
                        max_point = (x, y, z)
                        print(f'new max value: {max_value:.2f} at {max_point}')

    
            
            if value > max_value:
                max_value = value
                x = hexapod.position[0]
                y = hexapod.position[1]
                z = hexapod.position[2]
                max_point = (x, y, z)
                print(f'new max value: {max_value:.2f} at {max_point}')

            path_points_list.append((hexapod.position[1], hexapod.position[2]))  # Collect path points

        center = max_point
        print(f'finished iteration, new center: {center}')
        return center, path_points_list

    def refine_search(initial_point, initial_step_size = 1, refinement_factor = 2, max_iterations = 3, test_slice = None):
        step_size = initial_step_size
        center = initial_point
        all_path_points = [] # testing visualization
      
        for _ in range(max_iterations):
            # Hexapod moves along the path points, which are relative
            # range and grid_size are formatted in a way so it fits the path creation
            y_range = (-5*step_size, 5*step_size) # 5 mm in each direction
            z_range = (-5*step_size, 5*step_size)
            
            grid_size = (0, y_range[1] - y_range[0], z_range[1] - z_range[0])

            center, path_points_list = grid_search(center, grid_size, step_size)
            all_path_points.extend(path_points_list)
            step_size /= refinement_factor

        return center, all_path_points

         
    # 2D search for beam center (one slice)
    # Assuming the beam center has the maximal intensity

    centers = []

    step_size = (spacing, 1, 1)
    grid_size = ((num_centers-1)*spacing,0 , 0)

    x_path_points, _ = generate_snake_path(grid_size, step_size)    
    print(f'Path Points: \n {x_path_points}')


    for i in range(len(x_path_points)):

        if test_slices is not None:
            slice_1_2 = (test_slices["1"], test_slices["11"])
            test_slice = slice_1_2[i]

            y = test_slice["points"][:, 1]
            z = test_slice["points"][:, 2]
            intensities = test_slice["sum_values"]

            plt.scatter(y, z, c = intensities, s = 30, cmap='viridis')
            plt.colorbar(label='Intensity')


        print(f'!!!searching for center {i+1}/{num_centers}')
        center, all_path_points = refine_search(hexapod.position, test_slice = test_slice)
        centers.append(center)
        
        last_point = hexapod.position
        next_point = (x_path_points[i][0], x_path_points[i][1], x_path_points[i][2], 0, 0, 0)
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        hexapod.move(next_relative_position, flag = "relative")

        if test_slices is not None: # used for testing
            hexapod.position += next_relative_position
        
        # TODO Plotting maybe in GUI later?
        all_path_points = np.array(all_path_points)
        plt.plot(all_path_points[:, 0], all_path_points[:, 1], 'x-', color = 'black', markersize = 1)
        plt.scatter(center[1], center[2],marker = "x" ,color = 'red', s = 30)
        plt.show()


    return centers



def align_center(sensor, hexapod, depth = 0):
    # FUNCION ONLY USED FOR TESTING


    # allign beam to center of sensor recursivly
    # assumes the sensor detects the beam
    resolutions = [0.1, 0.01] # also use [0.1, 0.01, 0.001, 0.0001]

    if depth == len(resolutions):
        return True

    step_size = resolutions[depth]

    iterations = 0
    center = 0.5

    aligned = False

    while iterations < 50:
        iterations += 1

        #signal = sensor.get_signal() 
        if sensor.xpos is None or sensor.ypos is None:
            sensor.get_test_signal()


        print(f'Signal x: {sensor.xpos}, y: {sensor.ypos}')
        plt.plot(sensor.xpos, sensor.ypos, 'o')
        print(f'Hex Position: {hexapod.position}')

        if sensor.xpos > center+step_size:
            hexapod.move([-step_size, 0, 0, 0, 0, 0], flag = "relative") # TODO xpos and ypos changes only for testing purposes
            #sensor.xpos -= step_size
            
        elif sensor.xpos < center-step_size:
            hexapod.move([step_size, 0, 0, 0, 0, 0], flag = "relative")
            #sensor.xpos += step_size
        
        elif sensor.ypos > center+step_size:
            hexapod.move([0, 0, -step_size, 0, 0, 0], flag = "relative")
            #sensor.ypos -= step_size
            
        elif sensor.ypos < center-step_size:
            hexapod.move([0, 0, step_size, 0, 0, 0], flag = "relative")
            #sensor.ypos += step_size

        else:
            align_center(sensor, hexapod, depth+1)
            aligned = True
            break

    return aligned

def fine_alignment(sensor, hexapod):
    
    aligned = False
       

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(sensor.xpos, sensor.ypos, 'o')

    ax.set_xlabel('X Position')
    ax.set_ylabel('Y Position')
    ax.set_title('Sensor Output')
    ax.grid(True)
    ax.legend(['Signal Position'])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    aligned = align_center(sensor, hexapod)
        
    plt.show()
    print(f'Aligned: {aligned}')
    print(f'Final Position: {sensor.xpos}, {sensor.ypos}')

    return aligned

def rough_alignment(sensor, hexapod, probe):
    aligned = False
    
    hexapod.move_to_default_position()

    return aligned


if __name__ == "__main__":
    
    sensor = Sensor()
    hexapod = Hexapod()
    
    path = r'C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\Experiment_data\Default_2024-12-28_23-54-04.h5'
    data = load_data(path)
    
    test_slices = data["Visualization"]["Slices"]["vertical"]

    centers = find_beam_centers(sensor, hexapod, test_slices = test_slices)
    print(centers)


    #print(hexapod.connect_sockets())
    #print(hexapod.move_to_default_position())

    #aligned = fine_alignment(sensor, hexapod)
    #print(aligned)



