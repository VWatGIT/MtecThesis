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

    x = marker_tvecs[1] + unique_tvecs[0]
    y = marker_tvecs[0] + unique_tvecs[1]
    z = marker_tvecs[2] * (-1) + unique_tvecs[2]

    U = V = W = 0

    """
    # left out for now
    U = marker_rvecs[0] + unique_rvecs[0]
    V = marker_rvecs[1] + unique_rvecs[1]
    W = marker_rvecs[2] + unique_rvecs[2]
    """

    return [x, y, z, U, V, W]
    
def relative_hexapod_delta_position(pos1, pos2):
    """
    calculate the movement of the hexapod to move from pos1 to pos2
    pos1: photo diode array position
    pos2: probe tip position

    --> Hexapod goes from pos1 to pos2
    """

    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    dz = pos2[2] - pos1[2]
    dU = pos2[3] - pos1[3]
    dV = pos2[4] - pos1[4]
    dW = pos2[5] - pos1[5]

    return [dx, dy, dz, dU, dV, dW]


if __name__ == "__main__":
    #example Camera Matrix and Distortion Coefficients

    default_mtx = np.array((1000, 0.0, 900, 0.0, 1000, 600, 0.0, 0.0, 1.0)).reshape(3, 3)
    default_dist = np.array((-0.1, 0.59, 0.01, 0.02, -0.86))
    
    sensor = Sensor()
    probe = Probe()

    sensor.marker_tvecs = np.array((-8.9e-06, -1.3e-01, 3.1e-01))
    probe.marker_tvecs= np.array((0.008, -0.006,  0.3))

    sensor.photo_diode_array_position = translate_marker_vecs_to_position(sensor.marker_tvecs, sensor.marker_rvecs, sensor.unique_tvecs, sensor.unique_rvecs)
    probe.position = translate_marker_vecs_to_position(probe.marker_tvecs, probe.marker_rvecs, probe.unique_tvecs, probe.unique_rvecs)

    print(f"mtx: \n {default_mtx} \n")
    print(f"dist: {default_dist} \n")

    print(f"sensor position: {sensor.photo_diode_array_position}")
    print(f"probe position: {probe.position} \n")


    delta_pos = relative_hexapod_delta_position(sensor.photo_diode_array_position, probe.position)
    print(f"delta position: {delta_pos}")