import numpy as np
from sklearn.linear_model import LinearRegression

from Python_Skripts.Testing_Scripts.rotate_points import get_rotation_matrix



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
    pass



