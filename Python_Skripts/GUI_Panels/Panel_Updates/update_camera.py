import time
from Python_Skripts.Function_Groups.marker_detection import detect_markers
from Python_Skripts.Function_Groups.probe_tip_detection import draw_probe_tip
import cv2
import numpy as np


def update_camera(root):
        while root.camera_object.updating:      
            if root.camera.IsOpen() is True:
                try:
                    root.toggle_camera_var.set(1) # if camera is opened by other means than toggle button
                    image = root.camera_object.capture_image()

                    if root.draw_markers_var.get() == 1:

                        mtx = root.camera_object.mtx
                        dist = root.camera_object.dist
                        sensor_marker_size = root.sensor.marker_size
                        probe_marker_size = root.probe.marker_size 

                        marker_size = sensor_marker_size # for now assume same size TODO implement different sizes
                        
                        # marker drawn in detect markers
                        image, marker_rvecs, marker_tvecs = detect_markers(image, marker_size, mtx, dist)

                        if root.camera_object.camera_calibrated:
                            if len(marker_tvecs) > 0 and len(marker_rvecs) > 0 :
                                root.sensor.marker_rvecs = marker_rvecs[root.sensor.marker_id]
                                root.sensor.marker_tvecs = marker_tvecs[root.sensor.marker_id]
                                root.probe.marker_rvecs = marker_rvecs[root.probe.marker_id]
                                root.probe.marker_tvecs = marker_tvecs[root.probe.marker_id]

                                print("Sensor Marker tvecs: ", root.sensor.marker_tvecs)
                                print("Probe Marker tvecs: ", root.probe.marker_tvecs)

                    if root.draw_probe_tip_var.get() == 1:
                        image = draw_probe_tip(image, root.probe.probe_tip_position_in_camera_image)

                    if root.draw_checkerboard_var.get() == 1:
                        image = draw_calibration(root, image)


                    # Update Camera Image
                    canvas = root.camera_plot_frame.canvas
                    ax = canvas.figure.axes[0]
                    
                    ax.clear()
                    ax.imshow(image)
                    canvas.draw()

                    #time.sleep(root.camera_object.update_frequency/1000)
                except Exception as e:
                    root.camera_object.updating = False
                    root.log.log_event("Camera Update Error: " + str(e))
                    pass
            else:
                root.toggle_camera_var.set(0) # if camera is closed by other means than toggle button
        

def draw_calibration(root, image):
    
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    
    # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
    objp = np.zeros((root.camera_object.checkerboard_dimensions[0] * root.camera_object.checkerboard_dimensions[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:root.camera_object.checkerboard_dimensions[0], 0:root.camera_object.checkerboard_dimensions[1]].T.reshape(-1, 2)
    
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, root.camera_object.checkerboard_dimensions, None)

    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        cv2.drawChessboardCorners(image, root.camera_object.checkerboard_dimensions, corners2, ret)

    return image