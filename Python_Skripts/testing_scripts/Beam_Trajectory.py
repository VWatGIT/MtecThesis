import numpy as np
from Python_Skripts.Function_Groups.data_handling import load_data
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.spatial.transform import Rotation as R
'''
def get_theta_list(all_beam_points):
    # Project all points onto the x-y plane
    all_beam_points = all_beam_points[:,1:]

    theta_list = []
    for point in all_beam_points:
        x = point[0]
        y = point[1]
        
        if np.isclose(x, 0):
            theta_i = 0
        else:
            theta_i = np.degrees(np.arctan(y/x))

        theta_list.append(theta_i)   

    theta_list = np.array(theta_list)
    return theta_list

def plot_theta(theta_list, all_beam_points, intensities):
    all_beam_points = all_beam_points[:,1:]

    	
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.scatter(all_beam_points[:,0], all_beam_points[:,1], c=intensities)
    ax2.scatter(theta_list, intensities, s = 1)
    ax2.scatter(*get_unique(theta_list, intensities), color='red', s=5) 

    ax2.set_xlabel('theta')
    ax2.set_ylabel('intensity')
    ax2.set_xlim(-180, 180)


    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_aspect('equal')

    

    plt.show()

def get_unique(theta_list, intensities):
    unique_thetas, indices = np.unique(theta_list, return_index=True)
    max_intensities = np.zeros_like(unique_thetas)

    for i, theta in enumerate(unique_thetas):
        max_intensities[i] = np.max(intensities[theta_list == theta])

    return unique_thetas, max_intensities

def get_theta(data):	
    all_beam_points, intensities = get_all_points_and_intensities(data)


    theta_list = get_theta_list(all_beam_points)

    theta = np.average(theta_list, weights=intensities**2)

    plot_theta(theta_list, all_beam_points, intensities)
    
    return theta

def plot_phi(theta, all_beam_points, intensities):
    rotation = R.from_euler('z', theta, degrees=True)
    rotated_points = []
    for point in all_beam_points:
        point = rotation.apply(point)
        rotated_points.append(point)
    rotated_points = np.array(rotated_points)

    plt.scatter(rotated_points[:,0], rotated_points[:,2], c=intensities)
    plt.show()

def get_phi_list(all_beam_points, theta):
    # Project all points onto the phixy -z plane
    rotation = R.from_euler('z', theta, degrees=True)
    phi_list = []

    for point in all_beam_points:
        point = rotation.apply(point)
        x = point[0]
        z = point[2] 
        
        if np.isclose(x, 0):
            phi_i = 0
        else:
            phi_i = np.degrees(np.arctan(z/x))

        phi_list.append(phi_i)   

    phi_list = np.array(phi_list)
    return phi_list

def get_phi(data, theta):
    all_beam_points, intensities = get_all_points_and_intensities(data)

    phi_list = []
    phi_list = get_phi_list(all_beam_points, theta)

    phi = np.average(phi_list, weights=intensities**2)

    plot_phi(theta, all_beam_points, intensities)
    return phi

'''    

# DONT use this approach, refinement center search promises better results


def get_all_points_and_intensities(data):
    all_points = []
    all_intensities = []

    for key in data['Measurements'].keys():
        point = np.array(data['Measurements'][key]['Measurement_point'])
        intensities = np.array(data['Measurements'][key]['Signal_sum'])
        all_points.append(point)
        all_intensities.append(intensities)

    all_points = np.array(all_points)
    all_intensities = np.array(all_intensities)

    return all_points, all_intensities
def transform_points(all_points, intensities, origin = [0, 0, 0]):
    # TODO pass origin from gui
    # all_points are in the form [x, y, z]
    # x is the general beam direction [z]
    # transformed_points are in the form [theta, phi, z]
    transformed_points = []
    transformed_intensities= []
    z_max = np.max(np.abs(all_points[:,0]))
    y_max = np.max(np.abs(all_points[:,1]))
    x_max = np.max(np.abs(all_points[:,2]))

    for point, intensity in zip(all_points,intensities):
        x = point[2] + origin[2]
        y = point[1] + origin[1]
        z = point[0] + origin[0]
        

        '''
        r = np.sqrt(x**2 + y**2 + z**2)
        if x == 0 and y == 0:
            continue
        
        theta = np.degrees(np.arccos(z/r))  # Azimuthal angle
        phi = np.degrees(np.arccos(x/np.sqrt(x**2 + y**2)))   # Polar angle
        '''

        if z == 0:
            continue

        theta = np.degrees(np.arctan(x/z))
        phi = np.degrees(np.arctan(y/z))
        r = np.sqrt(x**2 + y**2 + z**2)

    
        transformed_points.append([theta, phi, r])
        transformed_intensities.append(intensity)

        '''
        if r < z_max or r< y_max or r < x_max:
            transformed_points.append([theta, phi, r])
            transformed_intensities.append(intensity)
        '''
            
    transform_points = np.array(transformed_points)
    intensities = np.array(intensities)

    return transform_points, transformed_intensities
def scale_intensities(points, intensities, w_0 = 1e-3, wavelength = 1000e-9):
    scaled_intensities = []

    for intensity, point in zip(intensities, points):
        r = point[2]
        factor = 1 + (r / (np.pi * w_0**2 / wavelength))**2
        scaled_intensity = intensity *factor
        scaled_intensities.append(scaled_intensity)
    scaled_intensities = np.array(scaled_intensities)

    return scaled_intensities

def remove_zero_intensity_points(points, intensities, active = True, tolerance = 1e-12):
    
    # remove points with intensity near 0
    if active:
        mask = ~np.isclose(intensities, 0, atol = tolerance)
        points = points[mask]
        intensities = intensities[mask]

    return points, intensities
def weigh_intensites_theta_phi(points, intensities):
    # remove points with intensity 0
    points, intensities = remove_zero_intensity_points(points, intensities)

    theta = points[:,0]
    phi = points[:,1]

    # Now take the weighted average of theta and phi
    theta = np.average(theta, weights=intensities**2)
    phi = np.average(phi, weights=intensities**2)

    return theta, phi

def calculate_theta_phi(data, w_0= 1e-3, wavelength = 1000e-9):
    all_points, intensities = get_all_points_and_intensities(data)
    transformed_points, intensities = transform_points(all_points, intensities)
    scaled_intensities = scale_intensities(all_points, intensities, w_0=w_0, wavelength= wavelength)
    filtered_points, filtered_intensities = remove_zero_intensity_points(transformed_points, scaled_intensities, active = False)
    theta, phi = weigh_intensites_theta_phi(filtered_points, filtered_intensities)
    deviation_magnitude = np.sqrt(theta**2 + phi**2)
    trajectory = get_trajectory(theta, phi)
    
    data['Visualization']['Beam_Models']['Measured_Beam']['theta'] = theta
    data['Visualization']['Beam_Models']['Measured_Beam']['phi'] = phi
    data['Visualization']['Beam_Models']['Measured_Beam']['trajectory'] = trajectory
    data['Visualization']['Beam_Models']['Measured_Beam']['deviation'] = deviation_magnitude

    return theta, phi, deviation_magnitude
def plot_theta_phi(data, ax = None):
    all_points, intensities = get_all_points_and_intensities(data)
    transformed_points, intensities = transform_points(all_points, intensities)
    scaled_intensities = scale_intensities(all_points, intensities)
    transformed_points, scaled_intensities = remove_zero_intensity_points(transformed_points, scaled_intensities, active = False)

    if data['Visualization']['Beam_Models']['Measured_Beam']['theta'] is not None:
        theta = data['Visualization']['Beam_Models']['Measured_Beam']['theta']
        phi = data['Visualization']['Beam_Models']['Measured_Beam']['phi']

    # plot
    if ax is None:
        fig, ax = plt.subplots()
    ax.scatter(transformed_points[:,0], transformed_points[:,1], c = scaled_intensities, s= 10, theta=0.3)
    ax.scatter(theta, phi, color = 'red', s = 20)
    ax.set_xlabel('theta')
    ax.set_ylabel('phi')
    ax.set_aspect('equal')
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)
    ax.grid()

    
def get_trajectory(theta, phi):
    default_trajectory = np.array([1, 0, 0])
    rotation = R.from_euler('yz', [theta, phi], degrees=True)
    trajectory = rotation.apply(default_trajectory)
    return trajectory

if __name__ == "__main__":
    #file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/Simulated_straight.h5'
    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/angle_10_20.h5'
    #file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/Ingo_1.h5'
    data = load_data(file_path) 

    # NEW trajectory calculation
    theta, phi, deviation_magnitude = calculate_theta_phi(data)
    print("theta =",theta)
    print("phi =",phi)
    print("deviation_magnitude =",deviation_magnitude)

    plot_theta_phi(data)
    plt.show()


    