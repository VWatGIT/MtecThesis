import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

from .trajectory import get_rotation_matrix

class GaussBeam:
    def __init__(self, wavelength = 1300e-9, w_0 = 1e-3, I_0 = 6.37e+04):
        self.wavelength = wavelength # lambda in m ?  
        self.w_0 = w_0 # Beam radius at z = 0
        self.I_0 = I_0 # Intensity at z = 0, r = 0
        self.z_r = np.pi * w_0**2 / wavelength # Rayleigh length

        self.theta = self.w_0 / self.z_r

        self.theta = 0
        self.phi = 0
        self.default_trj = [1, 0, 0]
        self.trj = self.default_trj

    def set_Trj(self, theta, phi):
        self.theta = theta
        self.phi = phi
        
        rotation = R.from_euler('zy', [theta,phi], degrees=True)
        self.trj = rotation.apply(self.default_trj)
       

    def get_Intensity(self, r= None, z= None, point = None):

        if np.all(self.trj != self.default_trj) and point is not None:
            # Simulate angled beam
            rotation_matrix = get_rotation_matrix(self.default_trj, self.trj)
            point = np.dot(point, rotation_matrix.T)

        if point is not None:
            # convert path coordinates to zylindrical coordinates
            r = np.sqrt(point[1]**2 + point[2]**2)*1e-3 # convert to mm
            z = -point[0]*1e-3 # convert to mm  flip the x coordinate to match the coordinate system
            # TODO check for correct trajectory

        w_z = self.get_Beam_Radius(z)
        I_rz = self.I_0 * (self.w_0 / w_z)**2 * np.exp(-2 * r**2 / w_z**2)
        return I_rz
    
    def get_Beam_Radius(self, z):
        w_z = self.w_0 * np.sqrt(1 + (z / self.z_r)**2)
        return w_z
    
    def get_Bending_Radius(self, z):
        R_z = z * (1 + (self.z_r / z)**2)
        return R_z
    

if __name__ == "__main__":

    gauss_beam = GaussBeam()
    
    '''
    # Parameter
    P = 100e-3  # Leistung in Watt (100mW)
    w_0 = 1e-3  # Strahltaille in Meter (1mm)

    # Berechnung der Intensität im Zentrum des Strahls
    I_0 = 2 * P / (np.pi * w_0**2)
    print(f"Die Intensität im Zentrum des Strahls beträgt {I_0:.2e} W/m^2")
    '''

    # Test at z = 0 and z = 1
    z = np.arange(5)

    fig, ax = plt.subplots()
    ax.set_xlabel('r [m]')
    ax.set_ylabel('I [W/m^2]')
    ax.set_title('Intensity of Gauss Beam')

    for i in range(len(z)):
        r = np.linspace(-2*gauss_beam.w_0, 2*gauss_beam.w_0, 100)
        I_rz = gauss_beam.get_Intensity(r = r, z = z[i])
        ax.plot(r, I_rz, label = 'z = ' + str(z[i]) + ' m')
        
    ax.legend()
    plt.show()
    

