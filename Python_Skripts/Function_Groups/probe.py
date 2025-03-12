
from configparser import ConfigParser
import os
import numpy as np
import cv2

class Probe():
    def __init__(self):

        # Load Configuration
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_path)

        self.marker_id = config.getint('Probe', 'marker_id')
        self.marker_size = config.getfloat('Probe', 'marker_size')

        # only z cooridnate of tvecs relevant
        self.unique_rvecs = list(map(float, config.get('Probe', 'unique_rvecs').split(',')))
        self.unique_tvecs = list(map(float, config.get('Probe', 'unique_tvecs').split(',')))

        self.marker_tvecs = [None, None, 1] # todo change back to None 
        self.marker_rvecs = [None, None, None] # rotation of marker not relevant as its very small

        self.position = None # tip in hexapod coordinates relative to camera position

        self.probe_tip_position_in_camera_image = None
        self.probe_tip_position = None # in camera coordinates

        self.probe_detected = False
        self.marker_detected = False


    def set_marker_vecs(self, marker_tvecs, marker_rvecs):
        self.marker_tvecs = marker_tvecs
        self.marker_rvecs = marker_rvecs
        if marker_tvecs is not None and marker_rvecs is not None:
            self.marker_detected = True


    def save_probe_position(self, camera_object, position = None):
        if position is None:
            position = self.probe_tip_position_in_camera_image

        if camera_object.camera_calibrated is True:
            self.probe_tip_position = self.translate_probe_tip(position, camera_object.mtx, camera_object.dist)
            self.probe_detected = True
        else:
            self.probe_detected = False


    def translate_probe_tip(self, probe_tip_position, mtx, dist):
        self.probe_tip_position = probe_tip_position

        # markers need to be detected before probe tip can be translated
        z = self.marker_tvecs[2] + self.unique_tvecs # add unique z coordinate

        # Step 1: Undistort the pixel coordinates
        undistorted_pixel = cv2.undistortPoints(np.array([self.probe_tip_position], dtype=np.float32), mtx, dist, P=mtx)

        # Step 2: Convert to normalized image coordinates
        undistorted_pixel_with_1 = np.append(undistorted_pixel[0][0], 1)  # Append 1 to the undistorted pixel coordinates
        inv_mtx = np.linalg.inv(mtx)  # Calculate the inverse of the camera matrix
        normalized_image_coords = inv_mtx.dot(undistorted_pixel_with_1)  # Multiply the inverse camera matrix with the undistorted pixel coordinates

        # Step 3: Scale by the z-value
        camera_coords = normalized_image_coords * z # postition in camera coordinate system

        return camera_coords


    def __repr__(self):
        return f"Probe(position={self.position}, rotation={self.rotation})"


if __name__ == "__main__":
    
    default_mtx = np.array((1000, 0.0, 900., 0.0, 1000, 600., 0.0, 0.0, 1.0)).reshape(3, 3)
    default_dist = np.array((-0.1, 0.59, 0.01, 0.02, -0.86))

    #print(f"default_mtx: \n {default_mtx}")

    probe = Probe()
    probe.marker_tvecs = [None, None, 100]


    probe_tip_position = probe.translate_probe_tip((100, 100), default_mtx, default_dist)
    print(f"probe tip position: {probe_tip_position}")
