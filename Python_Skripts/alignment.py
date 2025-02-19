from Object3D import Sensor, Hexapod
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from CreatePath import generate_snake_path
from data_handling import load_data
from rotate_points import get_rotation_matrix
from mpl_toolkits.mplot3d import Axes3D


def find_beam_centers(sensor, hexapod, spacing = 1/3, num_centers = 4, test_slices = None):
     #TODO decide on spacing and number of centers


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
            next_point = np.array((path_points[i][0] + initial_point[0], path_points[i][1] + initial_point[1], path_points[i][2] + initial_point[2], 0, 0, 0))
            next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
            hexapod.move(next_relative_position, flag = "relative")
            last_point = next_point

            signal = sensor.get_signal()
            value = signal.sum

            if test_slice is not None:
                # simulate sensor signal
                # find nearest point in test_slice
                test_points = test_slice["points"][:, :3]

                for i, point in enumerate(test_points):
                    if np.allclose(point[1:], next_point[1:3], atol=step_size[1]/2):
                        value = test_slice["sum_values"][i]
                        #print(f"near point found with value {value}")
                    else:
                        value = 0
                    
                    if value > max_value:
                        max_value = value
                        x = hexapod.position[0]
                        y = hexapod.position[1]
                        z = hexapod.position[2]
                        max_point = (x, y, z)
                        #print(f'new max value: {max_value:.2f} at {max_point}')



            if value > max_value:
                max_value = value
                x = hexapod.position[0]
                y = hexapod.position[1]
                z = hexapod.position[2]
                max_point = (x, y, z)
                #print(f'new max value: {max_value:.2f} at {max_point}')

            path_points_list.append((hexapod.position[1], hexapod.position[2]))  # Collect path points

        center = max_point
        print(f'finished iteration, new center: {center}')
        return center, path_points_list

    def refine_search(initial_point, initial_step_size = 1, refinement_factor = 2, max_iterations = 3, test_slice = None):
        step_size = initial_step_size
        initial_hexapod_position = initial_point
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

        hexapod.move(initial_hexapod_position, flag = "absolute") # return to initial position after finsished search


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
            slice_1_2 = (test_slices["1"], test_slices["4"], test_slices["7"], test_slices["11"])
            test_slice = slice_1_2[i]

            y = test_slice["points"][:, 1]
            z = test_slice["points"][:, 2]
            intensities = test_slice["sum_values"]

            plt.scatter(y, z, c = intensities, s = 30, cmap='viridis')
            plt.colorbar(label='Intensity')


        print(f'!!!searching for center {i+1}/{num_centers}')

        last_point = hexapod.position
        next_point = (x_path_points[i][0], x_path_points[i][1], x_path_points[i][2], 0, 0, 0)
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        hexapod.move(next_relative_position, flag = "relative")

        center, all_path_points = refine_search(hexapod.position, test_slice = test_slice)
        centers.append(center)
        

        
        # TODO Plotting maybe in GUI later?
        all_path_points = np.array(all_path_points)
        plt.plot(all_path_points[:, 0], all_path_points[:, 1], 'x-', color = 'black', markersize = 1)
        plt.scatter(center[1], center[2],marker = "x" ,color = 'red', s = 30)
        
    plt.show()

    return centers

def calculate_angle_to_x_axis(trj, degrees = True):
    # with respect to the x-axis 
    # trj = (x, y, z) trajectory
    trj = np.array(trj)
    trj = trj / np.linalg.norm(trj)    

    x = trj[0]
    y = trj[1]
    z = trj[2]

    r = np.sqrt(y**2 + z**2)

    phi = np.arctan2(np.abs(x), np.abs(r))

    if degrees:
        phi = np.degrees(phi)

    return phi

def calculate_angles(trajectory):
    #Spherical coodinates
    # trj = (x, y, z) trajectory
    # returns (phi, theta) in degrees
    # coordinates with respect to hexapod coordinate system
    
    
    # Normalize the trajectory vector
    trajectory = trajectory / np.linalg.norm(trajectory)

    # Extract the components of the trajectory vector
    x = trajectory[0]
    y = trajectory[1]
    z = trajectory[2]

    
    r = np.sqrt(x**2 + y**2 + z**2)

    phi = np.sign(y) * np.arccos(z/np.sqrt(x**2 + y**2))
    theta = np.arccos(x/r)
    
    angles = np.degrees(np.array([phi, theta]))
    return angles

def calculate_beam_trajectory_LR(center_points):
    center_points = np.array(center_points)
    # Fit a line to the center_points from the center of the first beam slice
    start_point = center_points[0]
    start_point = np.array([0, start_point[1], start_point[2]])

    # Shift the points to be relative to the start point
    shifted_points = center_points - start_point

    # Perform linear regression on the shifted points
    X = shifted_points[:, 0].reshape(-1, 1)  # Independent variable (x-axis)
    Y = shifted_points[:, 1]  # Dependent variable (y-axis)
    Z = shifted_points[:, 2]  # Dependent variable (z-axis)

    # Fit linear regression models
    reg_y = LinearRegression().fit(X, Y)
    reg_z = LinearRegression().fit(X, Z)

    # Get the coefficients (slopes) and intercepts
    slope_y = reg_y.coef_[0]
    #intercept_y = reg_y.intercept_
    slope_z = reg_z.coef_[0]
    #intercept_z = reg_z.intercept_

    # Define the trajectory vector
    trajectory_vector = np.array([1, slope_y, slope_z])

    # Invert the trajectory vector 
    trajectory_vector = -trajectory_vector

    # Normalize the trajectory vector
    trajectory_vector = trajectory_vector / np.linalg.norm(trajectory_vector)

    return trajectory_vector

def rotate_path(path_points, trj):
    # rotate each point in the path so it is "normal" to the beam trajectory
    path_points = np.array(path_points)
    rotated_path_points = []

    default_trj = np.array([-1, 0, 0])

    #default_angles = np.array([0, 180])
    #angles_to_rotate = default_angles - angles

    for point in path_points:
        rotation_matrix = get_rotation_matrix(default_trj, trj)
        
        rotated_point = np.dot(point, rotation_matrix.T)
        rotated_path_points.append(rotated_point)
        
    return np.array(rotated_path_points)

# REWORK Functions:

def align_center(sensor, hexapod, depth = 0):
    # FUNCION ONLY USED FOR TESTING
    # DONT USE IN THE FINAL VERSION


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
    
    #TODO uncomment later
    
    data = load_data(path)
    """
    test_slices = data["Visualization"]["Slices"]["vertical"]

    centers = find_beam_centers(sensor, hexapod, test_slices = test_slices)
    print(centers)
    """
    # test centers
    centers = [(0.0, 0.0, 0.0), (-0.3, 0.25, 0.0), (-0.6, 0.5, 0.0), (-1.0, 1.0, 0.0)]

    trj = calculate_beam_trajectory_LR(centers)
    print(trj)

    angle = calculate_angle_to_x_axis(trj)
    print(angle)

    angles = calculate_angles(trj)
    print(angles)

    path = data["3D"]["path"]
    grid = data["3D"]["grid"]

    path, _ = generate_snake_path((1, 4, 4), (1, 1, 1))

    default_trj = np.array([-1, 0, 0])
    default_angles = calculate_angles(default_trj)
    print(default_angles)

    rotated_path = rotate_path(path, trj)
    

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(rotated_path[:, 0], rotated_path[:, 1], rotated_path[:, 2], '.-', color = 'blue', linewidth = 0.5)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Rotated Path')

    plt.show()


    #print(hexapod.connect_sockets())
    #print(hexapod.move_to_default_position())

    #aligned = fine_alignment(sensor, hexapod)
    #print(aligned)



