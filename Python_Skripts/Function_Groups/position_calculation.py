import numpy as np

from Python_Skripts.Function_Groups.probe import Probe
from Python_Skripts.Function_Groups.sensor import Sensor

"""
The origin of the marker_vecs coordinate system is at the camera's optical center.
The ( z )-axis points forward, along the camera's optical axis.
The ( x )-axis points to the right, parallel to the image plane.
The ( y )-axis points down, parallel to the image plane.
"""

def translate_marker_vecs_to_position(marker_tvecs, marker_rvecs, unique_tvecs = None, uniqe_rvecs = None):
    """
    camera y --> hexapod x + unique_tvecs[0]
    camera x --> hexapod y + unique_tvecs[1]
    camera z --> hexapod z * (-1) + unique_tvecs[2]

    unique_tvecs and r_vecs already in hexapod coordinates
    
    marker_r_vecs and unique_rvecs are assumed to be negligible
    this function will calculate the position of the photo diode array or probe_tip in hexapod coordinates 
    but still relative to camera_position, not absolut hexapod coordinates
    """

    if unique_tvecs is None:
        unique_tvecs = [0.0, 0.0, 0.0]
    if uniqe_rvecs is None:
        unique_rvecs = [0.0, 0.0, 0.0]

    print("marker_tevcs:" , marker_tvecs)
    print("unique_tvecs:" , unique_tvecs)

    x = marker_tvecs[1] # + unique_tvecs[0] # marker y is hexapod x TODO ?
    y = marker_tvecs[2] # + unique_tvecs[1] # marker x is hexapod y TODO fix
    z = marker_tvecs[0] # + unique_tvecs[2] 

    print("unique_tvecs applied: ", (x,y,z), "\n")

    U = V = W = 0


    """
    # left out for now
    U = marker_rvecs[1] + unique_rvecs[0]
    V = marker_rvecs[0] + unique_rvecs[1]
    W = marker_rvecs[2] + unique_rvecs[2]
    """

    return np.array((x, y, z, U, V, W))
    
def relative_hexapod_delta_position(pos1, pos2):
    """
    calculate the movement of the hexapod to move from pos2 to pos1
    pos1: photo diode array position    # from
    pos2: probe tip position            # to

    --> Hexapod should go goes from pos1 to pos2
    """

    # first transform camera coordinates to hexapod coordinates
    # sensor_position as origin
    pos1 = np.array(pos1)
    pos2 = np.array(pos2)

    delta_pos = pos1 - pos2 # TODO i am stupid please help
 

    return delta_pos


if __name__ == "__main__":
    #example Camera Matrix and Distortion Coefficients

    default_mtx = np.array((1000, 0.0, 900, 0.0, 1000, 600, 0.0, 0.0, 1.0)).reshape(3, 3)
    default_dist = np.array((-0.1, 0.59, 0.01, 0.02, -0.86))
    
    sensor = Sensor()
    probe = Probe()

    
    probe.marker_tvecs = np.array([20.8, -119.4, 270.8])
    sensor.marker_tvecs = np.array([17.7,  17.1, 286.8 ])
    expected_movement = [136.5, -3.1, 16.0]
    """

    probe.marker_tvecs = np.array([-10, 20, 30])
    sensor.marker_tvecs = np.array([10, 10, -30])
    expected_movement = np.array([20, -10, -60])
    """

    photo_diode_array_position = translate_marker_vecs_to_position(sensor.marker_tvecs, sensor.marker_rvecs, sensor.unique_tvecs, sensor.unique_rvecs)
    probe_tip_position = translate_marker_vecs_to_position(probe.marker_tvecs, probe.marker_rvecs, probe.unique_tvecs, probe.unique_rvecs)

    
    delta_pos = relative_hexapod_delta_position(photo_diode_array_position, probe_tip_position)
    print(f"expected movement: {expected_movement}")
    print(f"delta position: {delta_pos}")