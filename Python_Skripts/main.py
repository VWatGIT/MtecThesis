import numpy as np
from pypylon import pylon
import os
import scipy.io 
import cv2
import glob

# import function
from CaptureIMG import capture_image
from calibrate_camera import calibrate_camera
from detect_markers import detect_markers

import Object3D

def crop_image(image, top_left, bottom_right):

    x1, y1 = top_left
    x2, y2 = bottom_right
    image_array_image = image[y1:y2, x1:x2]
    return image_array_image

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse coordinates: ({x}, {y})")

# Initialize the camera
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

#camera.Width = 640
#camera.Height = 480
camera.Width.Value = 1920 
camera.Height.Value = 1200 

frames = 1000

checkerboard_size = (7, 4)
checkerboard_images = []
save_dir = r'C:\Users\mtec\Desktop\Thesis_Misc_Valentin\Python_Skripts\Checkerboard_Images' 
checkerboard_images = glob.glob(os.path.join(save_dir, '*.jpg'))

ret, mtx, dist, camera_rvecs, camera_tvecs = calibrate_camera(checkerboard_images, checkerboard_size)

for i in range(frames):
    image_array = capture_image(camera)
    
    # Detect ArUco markers and estimate their pose
    image_array, marker_rvecs, marker_tvecs = detect_markers(image_array, mtx, dist)
    
    #print(f"Marker rvecs: {marker_rvecs}")
    #print(f"Marker tvecs: {marker_tvecs}")

    cv2.imshow('image',image_array)    
    cv2.setMouseCallback('image', mouse_callback)
    # Check for a key press to terminate the program
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
camera.Close()