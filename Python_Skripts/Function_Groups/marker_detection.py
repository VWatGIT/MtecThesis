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
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50) # TODO use DICT_7x7_50 for higher accuracy
    parameters = cv2.aruco.DetectorParameters()
    #detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)
    # ids: [[1] [0]] !! why is it ordered like this

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
            cv2.drawFrameAxes(image, mtx, dist, rvecs[i], tvecs[i], marker_size* 3, 1)
        

    else:
        rvecs = []
        tvecs = []
    
    return image, rvecs, tvecs, ids


if __name__ == "__main__":
    from camera import Camera, save_checkerboard_images
    from hexapod import Hexapod
    from probe import Probe
    from sensor import Sensor
    from position_calculation import relative_hexapod_delta_position
    import matplotlib.pyplot as plt



    # reset hexapod to default position
    hexapod = Hexapod()
    rcv = hexapod.connect_sockets()
    print(f"connecting: {rcv}")
    rcv = hexapod.move_to_default_position()
    print(f"returning: {rcv}")

    sensor = Sensor()
    probe = Probe()

    camera = Camera()
    default_mtx = np.array([[1159.061367160494, 0.0, 959.5], [0.0, 1166.761872411369, 599.5], [0.0, 0.0, 1.0]])
    default_dist = np.array([-1.0747645746734102e-09, -1.0268535676044898e-06, -9.627468392549926e-12, -1.0691973772958522e-11, 3.057283326385777e-10])

    #path = r"Python_Skripts\Checkerboard_Images\checkerboard_1.jpg"
    #path = r'C:\Users\mtec\Desktop\Thesis_Misc_Valentin\Git_repository\MtecThesis\Python_Skripts\Checkerboard_Images\checkerboard_1.jpg'
    #image = cv2.imread(path)

    image = camera.capture_image()    

    image, rvecs, tvecs, ids = detect_markers(image, 16, default_mtx, default_dist)
    
    camera_center = (image.shape[1]//2, image.shape[0]//2)
    cv2.circle(image, camera_center, 5, (0, 0, 255), -1)
    
    probe_tip_position_in_camera_image = np.array((950, 440))
    cv2.circle(image, probe_tip_position_in_camera_image, 5, (0, 255, 0), -1)
    
    cv2.imshow("Image", image)
    cv2.waitKey(0)

    for i in range(len(ids)):
        if ids[i][0] == probe.marker_id:
            probe.set_marker_vecs(tvecs[i][0], rvecs[i][0])
            print(f"Probe with ID:  {ids[i]} | tvecs: {tvecs[i][0]}")
        if ids[i][0] == sensor.marker_id:
            sensor.set_marker_vecs(tvecs[i][0], rvecs[i][0])
            print(f"Sensor with ID: {ids[i]} | tvecs: {tvecs[i][0]}")

    probe.probe_tip_position_in_camera_image = probe_tip_position_in_camera_image

    photo_diode_array_position = sensor.apply_unique_tvecs() 
    probe_tip_position = probe.translate_probe_tip(probe.probe_tip_position_in_camera_image, default_mtx, default_dist)
    
    print("\n")
    print(f"photo_diode_array_position: {photo_diode_array_position}")
    print(f"probe_tip_position:         {probe_tip_position}")
    print("\n")
    print(f"diff:                       {photo_diode_array_position - probe_tip_position}")

    delta_movement = relative_hexapod_delta_position(photo_diode_array_position, probe_tip_position)
    
    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    
    ax.scatter(probe.marker_tvecs[0], probe.marker_tvecs[1], probe.marker_tvecs[2],marker = 'x', label='probe marker')
    ax.scatter(sensor.marker_tvecs[0], sensor.marker_tvecs[1], sensor.marker_tvecs[2],marker = 'x', label='sensor marker')
    
    ax.scatter(photo_diode_array_position[0], photo_diode_array_position[1], photo_diode_array_position[2], label='photo diode array')
    ax.scatter(probe_tip_position[0], probe_tip_position[1], probe_tip_position[2], label='probe tip', c = "green")
    
    delta_path = np.array([photo_diode_array_position, probe_tip_position])
    ax.plot(delta_path[:, 0], delta_path[:, 1], delta_path[:, 2], "--x",label='alignment path')
    
    ax.scatter(0, 0, 0, label=' camera origin', marker = '*', c = "red")
    ax.set_xlabel('Camera X | Hexapod -Y')
    ax.set_ylabel('Camera Y | Hexapod +X')
    ax.set_zlabel('Camera Z | Hexapod -Z')
    
    
    
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_aspect("auto")
    ax.grid(True)
    ax.legend()
    plt.show()
    
    
    
    
    print(f"delta movement:             {delta_movement}")
    delta_movement[0] = 0 # !!! dont crash

    #rcv = hexapod.move(delta_movement, flag='relative')
    #print(f"moving: {rcv}")

    
    


