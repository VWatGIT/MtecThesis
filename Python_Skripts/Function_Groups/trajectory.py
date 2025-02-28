import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from mpl_toolkits.mplot3d import Axes3D

from Python_Skripts.Function_Groups.path_creation import generate_snake_path
from Python_Skripts.Function_Groups.data_handling import load_data
from Python_Skripts.Testing_Scripts.rotate_points import get_rotation_matrix
from Python_Skripts.Function_Groups.hexapod import Hexapod
from Python_Skripts.Function_Groups.sensor import Sensor

from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_center_plot import update_beam_center_plot


def grid_search(root, data, initial_point, grid_size, step_size):
    max_value = -np.inf
    max_point = None
    
    step_size = (step_size, step_size, step_size)

    path_points, _ = generate_snake_path(grid_size, step_size)
    #print(f'Path Points: \n {path_points}')
    last_point = initial_point
    root.hexapod.move(initial_point, flag = "absolute")
    for i in range(len(path_points)):

        # As Path points are absolute, transform them to relative positions
        next_point = np.array((path_points[i][0] + initial_point[0], path_points[i][1] + initial_point[1], path_points[i][2] + initial_point[2], 0, 0, 0))
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        hexapod.move(next_relative_position, flag = "relative")
        last_point = next_point

        current_path_point = (hexapod.position[0], hexapod.position[1], hexapod.position[2])
        if root.simulate_var.get() == 1:
            value = root.gauss_beam.get_intensity(point = current_path_point)

        signal = root.sensor.get_signal()
        value = signal.sum


        if value > max_value:
            max_value = value
            x = hexapod.position[0]
            y = hexapod.position[1]
            z = hexapod.position[2]
            max_point = (x, y, z)
            #print(f'new max value: {max_value:.2f} at {max_point}')
        
        data['Alignment']['Center_Search']['Path_Points'].append(current_path_point) # Save path points
        update_beam_center_plot(root)
        

    max_point
    print(f'finished iteration, new center: {max_point}')
    return max_point

def refine_search(root, data, initial_point, initial_step_size = 1, refinement_factor = 2, max_iterations = 3):
    step_size = initial_step_size
    initial_hexapod_position = initial_point
    center = initial_point
    
    for _ in range(max_iterations):
        # Hexapod moves along the path points, which are relative
        # range and grid_size are formatted in a way so it fits the path creation
        y_range = (-5*step_size, 5*step_size) # 5 mm in each direction
        z_range = (-5*step_size, 5*step_size)
        
        grid_size = (0, y_range[1] - y_range[0], z_range[1] - z_range[0])

        center = grid_search(root, data, center, grid_size, step_size)
        step_size /= refinement_factor

    root.hexapod.move(initial_hexapod_position, flag = "absolute") # return to initial position after finsished search


    return center





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

def get_rotation_matrix(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (3x3) which when applied to vec1, aligns it with vec2.
    """
    a, b = normalize(vec1), normalize(vec2)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]],
                     [v[2], 0, -v[0]],
                     [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    return rotation_matrix

def normalize(v):
    return v / np.linalg.norm(v)

if __name__ == "__main__":
    from Python_Skripts.GUI_Panels.Movement_Procedures.find_beam_centers import find_beam_centers
    
    sensor = Sensor()
    hexapod = Hexapod()
    
    path = r"C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\Experiment_data\Default_2025-02-25_02-27-25.h5"
    #path = r'C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Experiment_data\Default_2024-12-28_23-54-04.h5'
    
   
    data = load_data(path)

    # TODO eveything below is old and doesnt work
    # TODO dont use test slices but simulated gauss beam 
    test_slices = data["Visualization"]["Slices"]["vertical"]

    centers = find_beam_centers(sensor, hexapod, test_slices = test_slices)
    print(centers)
    
    # test centers
    #centers = [(0.0, 0.0, 0.0), (-0.3, 0.25, 0.0), (-0.6, 0.5, 0.0), (-1.0, 1.0, 0.0)]

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



