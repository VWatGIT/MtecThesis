import numpy as np
from pypylon import pylon
import cv2
import glob
import os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt



def detect_markers(image, marker_size, mtx, dist):
 
    # Load the predefined dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)

    if ids is not None:
        # Estimate pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, mtx, dist)  # marker_size is the marker length in meters

        # Draw detected markers and their axes
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
    else:
        rvecs = []
        tvecs = []
    
    return image, rvecs, tvecs


if __name__ == "__main__":
    pass
    