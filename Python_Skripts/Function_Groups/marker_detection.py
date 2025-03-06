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
    #detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)

    if ids is not None:
        # Estimate pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, marker_size, mtx, dist)  # marker_size is the marker length in meters
        

        '''
        pip uninstall opencv-python -y
        pip uninstall opencv-contrib-python -y
        to use older version of opencv
        # pip install opencv-contrib-python==4.6.0.66
        for rvec, tvec in zip(rvecs, tvecs):
            cv2.solvePnP(objPoints, corners, mtx, dist)
                        
         #solvePnP(objPoints, corners.at(i), camMatrix, distCoeffs, rvecs.at(i), tvecs.at(i));
        '''
        
        # Draw detected markers and their axes
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
        # TODO comment out
        for i in range(len(ids)):
            cv2.drawFrameAxes(image, mtx, dist, rvecs[i], tvecs[i], marker_size* 1.5, 1)
        

    else:
        rvecs = []
        tvecs = []
    
    return image, rvecs, tvecs


if __name__ == "__main__":
    from camera import Camera, save_checkerboard_images
    from hexapod import Hexapod
    from probe import Probe
    from sensor import Sensor
    from position_calculation import relative_hexapod_delta_position, translate_marker_vecs_to_position

    camera = Camera()


    default_mtx = np.array([[1159.061367160494, 0.0, 959.5], [0.0, 1166.761872411369, 599.5], [0.0, 0.0, 1.0]])
    default_dist = np.array([-1.0747645746734102e-09, -1.0268535676044898e-06, -9.627468392549926e-12, -1.0691973772958522e-11, 3.057283326385777e-10])

    image = camera.capture_image()

    
    #path = r'C:\Users\mtec\Desktop\Thesis_Misc_Valentin\Git_repository\MtecThesis\Python_Skripts\Checkerboard_Images\checkerboard_1.jpg'
    #image = cv2.imread(path)
    

    image, rvecs, tvecs = detect_markers(image, 16, default_mtx, default_dist)
    camera_center = (image.shape[1]//2, image.shape[0]//2)
    cv2.circle(image, camera_center, 5, (0, 0, 255), -1)
    
    for i in range(len(tvecs)):
        print(f"Marker {i} tvec: {tvecs[i]}")

    cv2.imshow("Image", image)
    cv2.waitKey(0)

    # now calculate movement
    hexapod = Hexapod()
    sensor = Sensor()
    probe = Probe()

    probe.set_marker_vecs(tvecs[0][0], rvecs[0][0])
    sensor.set_marker_vecs(tvecs[1][0], rvecs[1][0])

    # skip adding unique tvecs for now

    photo_diode_array_position = translate_marker_vecs_to_position(sensor.marker_tvecs, sensor.marker_rvecs, sensor.unique_tvecs, sensor.unique_rvecs) 
    probe_tip_position = translate_marker_vecs_to_position(probe.marker_tvecs, probe.marker_rvecs, probe.unique_tvecs, probe.unique_rvecs)

    delta_movement = relative_hexapod_delta_position(photo_diode_array_position, probe_tip_position)
    delta_movement[0] = 0 # !!! dont crash

    print(f"delta movement: {delta_movement}")
    cv2.waitKey(0)

    rcv = hexapod.connect_sockets()
    print(f"connecting: {rcv}")
    rcv = hexapod.move_to_default_position()
    print(f"returning: {rcv}")


#    rcv = hexapod.move(delta_movement, flag='relative')
 #   print(f"moving: {rcv}")


    


