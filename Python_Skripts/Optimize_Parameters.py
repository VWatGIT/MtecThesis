import numpy as np
from data_handling import load_data
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation as R

'''
Parameters:
p = [w_0, I_0, alpha, beta]

w_0: Beam radius at z = 0
I_0: Intensity at z = 0, r = 0
alpha: angle of beam
beta: angle of beam



'''

def get_Points(data):
    points = []
    for key in data['Measurements'].keys():
            point = data['Measurements'][key]['Measurement_point']
            points.append(point)
    return points
def get_Intensities(data):
    intensities = []
    for key in data['Measurements'].keys():
            intensity = data['Measurements'][key]['Signal_sum']
            intensities.append(intensity)
    return intensities

def get_Beam_Radius(z, w_0):
    wavelength = 1000e-9
    z_r = np.pi * w_0**2 / wavelength

    w_z = w_0 * np.sqrt(1 + (z / z_r)**2)
    return w_z
def get_I(v, I_0, w_0):
    x = v[0]
    y = v[1]
    z = v[2]
    r = np.sqrt(x**2 + y**2)

    w_z = get_Beam_Radius(z, w_0)
    I_rz = I_0 * (w_0 / w_z)**2 * np.exp(-2 * r**2 / w_z**2)
    return I_rz

def I_p(v, p):
    # v = [x, y, z]
    # p = [w_0, I_0, alpha, beta]
    w_0 = p[0]
    i_0 = p[1]
    alpha = p[2]
    beta = p[3]

    # Rotate the point
    rotation = R.from_euler('xy', [alpha,beta], degrees=True)      
    rotation.apply(v)
    
    # Calculate the intensity
    Intensity = get_I(v, i_0, w_0) 
    return Intensity

def func_to_be_minimized(p, points, intensities):
    sum = 0

    for i in range(len(points)):
        sum += np.sum(intensities[i] - I_p(points[i], p))

    return sum

if __name__ == "__main__":

    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/simulated_at_angle.h5'
    data = load_data(file_path)     

    points = get_Points(data)
    intensities = get_Intensities(data)

    # Initial guess
    w_0 = 1e-3
    i_0 = 6.37e+04
    alpha = 10
    beta = 10

    p0 = [w_0, i_0, alpha, beta]

    # Fit the parameters
    result = least_squares(func_to_be_minimized, p0, args=(points, intensities))

    # Extract the optimized parameters
    w_0_opt, I_0_opt, alpha_opt, beta_opt = result.x
    print(f"Optimized parameters: w_0={w_0_opt}, I_0={I_0_opt}, alpha={alpha_opt}, beta={beta_opt}")
