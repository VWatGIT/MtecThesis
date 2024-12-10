import numpy as np
from pypylon import pylon
import cv2
import glob
import os

def detect_markers(image, mtx, dist):
    """
    Detect ArUco markers in the image and estimate their pose.

    Parameters:
    image (numpy.ndarray): The input image.
    mtx (numpy.ndarray): Camera matrix.
    dist (numpy.ndarray): Distortion coefficients.

    Returns:
    image (numpy.ndarray): The image with detected markers and axes drawn.
    rvecs (list): Rotation vectors of the detected markers.
    tvecs (list): Translation vectors of the detected markers.
    """
    # Load the predefined dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)

    if ids is not None:
        # Estimate pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.016, mtx, dist)  # 0.016 is the marker length in meters

        # Draw detected markers and their axes
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
    else:
        rvecs = []
        tvecs = []
    
    return image, rvecs, tvecs
