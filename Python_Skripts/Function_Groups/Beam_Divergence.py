import numpy as np







if __name__ == '__main__':
    
    # Define the beam parameters
    w_0 = 1e-3 # mm
    wavelength = 1.3e-6 # mm


    z_r = np.pi*(w_0**2)/wavelength

    print(z_r)