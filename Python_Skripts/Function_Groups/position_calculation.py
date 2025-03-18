import numpy as np

from Python_Skripts.Function_Groups.probe import Probe
from Python_Skripts.Function_Groups.sensor import Sensor

"""
The origin of the marker_vecs coordinate system is at the camera's optical center.
The ( z )-axis points forward, along the camera's optical axis.
The ( x )-axis points to the right, parallel to the image plane.
The ( y )-axis points down, parallel to the image plane.
"""

    
def relative_hexapod_delta_position(pos1, pos2):
    """
    calculate the movement of the hexapod to move from pos2 to pos1
    bott position inputs are in camera coordinates
    
    pos1: photo diode array position    # from
    pos2: probe tip position            # to

    --> Hexapod should go goes from pos1 to pos2
    """

    # first transform camera coordinates to hexapod coordinates
    # sensor_position as origin
    pos1 = np.array(pos1)
    pos2 = np.array(pos2)

    delta = pos2 - pos1 
    # TODO check signs and coordinate tranformations
    x = delta[1]
    y = -delta[0] # -?
    z = -delta[2]
    
    delta_pos = np.array((x, y, z, 0, 0, 0)) # add 0s to get a hexapod position
    delta[0] -= 1 # 1mm tolerance
    return delta_pos


if __name__ == "__main__":
    #example Camera Matrix and Distortion Coefficients
    pass