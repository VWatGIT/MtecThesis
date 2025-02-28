
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

        self.marker_tvecs = [None, None, None] 
        self.marker_rvecs = [None, None, None] # rotation of marker not relevant as its very small

        self.position = None # tip in hexapod coordinates relative to camera position

        self.probe_tip_position_in_camera_image = (0, 0)
        self.probe_tip_position = None

        self.probe_detected = False
        self.marker_detected = False



    def set_detected_probe_position(self, position, camera_object):
        self.probe_tip_position_in_camera_image = position

        if camera_object.camera_calibrated is True:
                
            self.probe_tip_position = self.translate_probe_tip(position, camera_object.mtx, camera_object.dist)
            # refers to the probe tip position in camera coordinates
            self.probe_detected = True
        else:
            self.probe_detected = False


    def translate_probe_tip(self, probe_tip_position, mtx, dist):
        self.probe_tip_position = probe_tip_position

        z = self.marker_tvecs[2]
        
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
