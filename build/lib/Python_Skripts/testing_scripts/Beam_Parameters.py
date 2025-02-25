import numpy as np


'''
M_i --> Data to work with
I_i --> Intensities at Points i

L --> Beam Parameters
I_0 --> Intensity at z = 0, r = 0
w_0 --> Beam radius at z = 0
lambda --> Wavelength
(z_r --> Rayleigh length) can be calculated from w_0 and lambda
(Theta --> Divergence Angle) can be calculated from w_0 and z_r

trj --> Trajectory of the Beam (extra)

TASK: 
Go from M_i = I_i(X)
to L = (I_0, w_0, z_r, lambda, theta, trj)

using a function that takes M_i as input and returns L as output
'''

def get_Beam_Parameters(data):
    I_0 = get_I_0(data)
    w_0 = get_w_0(data)
    wavelength = get_wavelength(data)
    z_r = get_z_r(w_0, wavelength)
    theta = get_theta(w_0, z_r)
    
    
    trj = None
    
    return I_0, w_0, z_r, theta

def get_wavelength(data=None):
    wavelength = 1300e-9 #1300 [nm]
    # TELESTO SYSTEM WAVELENGTH
    # TODO: implement wavelength extraction from data
    return wavelength

def get_I_0(data):
    I_0 = None
    
    return I_0

def get_w_0(data):
    w_0 = None

    return w_0

def get_theta(w_0, z_r):
    theta = w_0 / z_r
    return theta

def get_z_r(w_0, wavelength):
    z_r = np.pi * w_0**2 / wavelength
    return z_r

if __name__ == "__main__": 
    wave_length = 1000e-9




    
