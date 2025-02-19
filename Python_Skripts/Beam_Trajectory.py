import numpy as np
from data_handling import load_data
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.spatial.transform import Rotation as R
'''
def get_alpha_list(all_beam_points):
    # Project all points onto the x-y plane
    all_beam_points = all_beam_points[:,1:]

    alpha_list = []
    for point in all_beam_points:
        x = point[0]
        y = point[1]
        
        if np.isclose(x, 0):
            alpha_i = 0
        else:
            alpha_i = np.degrees(np.arctan(y/x))

        alpha_list.append(alpha_i)   

    alpha_list = np.array(alpha_list)
    return alpha_list

def plot_alpha(alpha_list, all_beam_points, intensities):
    all_beam_points = all_beam_points[:,1:]

    	
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.scatter(all_beam_points[:,0], all_beam_points[:,1], c=intensities)
    ax2.scatter(alpha_list, intensities, s = 1)
    ax2.scatter(*get_unique(alpha_list, intensities), color='red', s=5) 

    ax2.set_xlabel('alpha')
    ax2.set_ylabel('intensity')
    ax2.set_xlim(-180, 180)


    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_aspect('equal')

    

    plt.show()

def get_unique(alpha_list, intensities):
    unique_alphas, indices = np.unique(alpha_list, return_index=True)
    max_intensities = np.zeros_like(unique_alphas)

    for i, alpha in enumerate(unique_alphas):
        max_intensities[i] = np.max(intensities[alpha_list == alpha])

    return unique_alphas, max_intensities

def get_alpha(data):	
    all_beam_points, intensities = get_all_points_and_intensities(data)


    alpha_list = get_alpha_list(all_beam_points)

    alpha = np.average(alpha_list, weights=intensities**2)

    plot_alpha(alpha_list, all_beam_points, intensities)
    
    return alpha

def plot_beta(alpha, all_beam_points, intensities):
    rotation = R.from_euler('z', alpha, degrees=True)
    rotated_points = []
    for point in all_beam_points:
        point = rotation.apply(point)
        rotated_points.append(point)
    rotated_points = np.array(rotated_points)

    plt.scatter(rotated_points[:,0], rotated_points[:,2], c=intensities)
    plt.show()

def get_beta_list(all_beam_points, alpha):
    # Project all points onto the betaxy -z plane
    rotation = R.from_euler('z', alpha, degrees=True)
    beta_list = []

    for point in all_beam_points:
        point = rotation.apply(point)
        x = point[0]
        z = point[2] 
        
        if np.isclose(x, 0):
            beta_i = 0
        else:
            beta_i = np.degrees(np.arctan(z/x))

        beta_list.append(beta_i)   

    beta_list = np.array(beta_list)
    return beta_list

def get_beta(data, alpha):
    all_beam_points, intensities = get_all_points_and_intensities(data)

    beta_list = []
    beta_list = get_beta_list(all_beam_points, alpha)

    beta = np.average(beta_list, weights=intensities**2)

    plot_beta(alpha, all_beam_points, intensities)
    return beta

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
    # transformed_points are in the form [alpha, beta, z]
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
        
        alpha = np.degrees(np.arccos(z/r))  # Azimuthal angle
        beta = np.degrees(np.arccos(x/np.sqrt(x**2 + y**2)))   # Polar angle
        '''

        if z == 0:
            continue

        alpha = np.degrees(np.arctan(x/z))
        beta = np.degrees(np.arctan(y/z))
        r = np.sqrt(x**2 + y**2 + z**2)

    
        transformed_points.append([alpha, beta, r])
        transformed_intensities.append(intensity)

        '''
        if r < z_max or r< y_max or r < x_max:
            transformed_points.append([alpha, beta, r])
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
def weigh_intensites_alpha_beta(points, intensities):
    # remove points with intensity 0
    points, intensities = remove_zero_intensity_points(points, intensities)

    alpha = points[:,0]
    beta = points[:,1]

    # Now take the weighted average of alpha and beta
    alpha = np.average(alpha, weights=intensities**2)
    beta = np.average(beta, weights=intensities**2)

    return alpha, beta

def calculate_alpha_beta(data, w_0= 1e-3, wavelength = 1000e-9):
    all_points, intensities = get_all_points_and_intensities(data)
    transformed_points, intensities = transform_points(all_points, intensities)
    scaled_intensities = scale_intensities(all_points, intensities, w_0=w_0, wavelength= wavelength)
    filtered_points, filtered_intensities = remove_zero_intensity_points(transformed_points, scaled_intensities, active = False)
    alpha, beta = weigh_intensites_alpha_beta(filtered_points, filtered_intensities)
    deviation_magnitude = np.sqrt(alpha**2 + beta**2)
    trajectory = get_trajectory(alpha, beta)
    
    data['Visualization']['Beam_Models']['Measured_Beam']['alpha'] = alpha
    data['Visualization']['Beam_Models']['Measured_Beam']['beta'] = beta
    data['Visualization']['Beam_Models']['Measured_Beam']['trajectory'] = trajectory
    data['Visualization']['Beam_Models']['Measured_Beam']['deviation'] = deviation_magnitude

    return alpha, beta, deviation_magnitude
def plot_alpha_beta(data, ax = None):
    all_points, intensities = get_all_points_and_intensities(data)
    transformed_points, intensities = transform_points(all_points, intensities)
    scaled_intensities = scale_intensities(all_points, intensities)
    transformed_points, scaled_intensities = remove_zero_intensity_points(transformed_points, scaled_intensities, active = False)

    if data['Visualization']['Beam_Models']['Measured_Beam']['alpha'] is not None:
        alpha = data['Visualization']['Beam_Models']['Measured_Beam']['alpha']
        beta = data['Visualization']['Beam_Models']['Measured_Beam']['beta']

    # plot
    if ax is None:
        fig, ax = plt.subplots()
    ax.scatter(transformed_points[:,0], transformed_points[:,1], c = scaled_intensities, s= 10, alpha=0.3)
    ax.scatter(alpha, beta, color = 'red', s = 20)
    ax.set_xlabel('alpha')
    ax.set_ylabel('beta')
    ax.set_aspect('equal')
    ax.set_xlim(-180, 180)
    ax.set_ylim(-180, 180)
    ax.grid()

    
def get_trajectory(alpha, beta):
    default_trajectory = np.array([1, 0, 0])
    rotation = R.from_euler('yz', [alpha, beta], degrees=True)
    trajectory = rotation.apply(default_trajectory)
    return trajectory

if __name__ == "__main__":
    #file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/Simulated_straight.h5'
    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/angle_10_20.h5'
    #file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/Ingo_1.h5'
    data = load_data(file_path) 

    # NEW trajectory calculation
    alpha, beta, deviation_magnitude = calculate_alpha_beta(data)
    print("alpha =",alpha)
    print("beta =",beta)
    print("deviation_magnitude =",deviation_magnitude)

    plot_alpha_beta(data)
    plt.show()


    