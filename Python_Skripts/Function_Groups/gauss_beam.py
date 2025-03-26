import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R

from Python_Skripts.Function_Groups.trajectory import get_rotation_matrix


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
        self.trj = self.default_trj.copy()

    def set_Trj(self, theta, phi):
        self.trj = self.default_trj.copy()
        self.theta = float(theta) # polar angle theta
        self.phi = float(phi)   # azimuthal angle phi
        
        # rotate the default trajectory
        rotation = R.from_euler('yx', [-self.theta,self.phi], degrees=True) # using physics convention for the angles
        new_trj = rotation.apply(self.trj)
        self.trj = new_trj

    def get_Intensity(self, r= None, z= None, point = None, shift = None):
        if np.any(self.trj != self.default_trj) and (point is not None):
            # Simulate angled beam
            rotation_matrix = get_rotation_matrix(self.default_trj, self.trj)
            point = np.dot(point, rotation_matrix.T)
            #print("simulated angle")

        if point is not None:
            # shift beam for testing TODO remove
            #print(point)
            try:
                beam_point = point.copy()
            except:
                beam_point = point

            if shift is not None:
                beam_point[0] += shift[0]
                beam_point[1] += shift[1]
                beam_point[2] += shift[2]

            # convert path coordinates to zylindrical coordinates
            r = np.sqrt(beam_point[1]**2 + beam_point[2]**2)*1e-3 # convert to mm
            z = -beam_point[0]*1e-3 # convert to mm  flip the x coordinate to match the coordinate system
            

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
    gauss_beam.set_Trj(45, 0)

    gauss_beam.get_Intensity(point = [0, 0, 0])


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
    

