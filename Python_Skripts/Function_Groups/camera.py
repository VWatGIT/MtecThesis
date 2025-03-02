import numpy as np
from pypylon import pylon
import cv2
import os
import tkinter as tk

import matplotlib.pyplot as plt
class Camera():
    def __init__(self):
        self.camera = None 
        self.create_camera() 
    
        # for zooming
        self.original_ylim = None
        self.original_xlim = None
        self._set_original_limits()

        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = None , None, None, None , None
        self.camera_connected = False
        self.camera_calibrated = False
        
        self.updating = False
        self.update_frequency = 10 #[ms] # set in config
        



        self.max_number_calibration_images = 10 # set in config
        self.num_calibration_images = tk.IntVar(value=0) # set in config to 
        self.calibration_images = []
        self.checkerboard_dimensions = (7, 4) # set in config
        self.checkerboard_size = 5  # set in config

        self.default_mtx = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]) #set in config
        self.default_dist = np.array([0.0, 0.0, 0.0, 0.0, 0.0]) # set in config
       
       
        self.use_default_calibration(startup = True)

    def _set_original_limits(self):
        fig, ax = plt.subplots()
        image = self.capture_image()
        ax.imshow(image)

        self.original_xlim = ax.get_xlim()
        self.original_ylim = ax.get_ylim()
        plt.close(fig)

    def reset_calibration(self):
        self.use_default_calibration(startup = True)
        self.calibration_images = []        

    def set_calibration_values(self, ret, mtx, dist, rvecs, tvecs):
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = ret, mtx, dist, rvecs, tvecs
        self.camera_calibrated = True

    def create_camera(self):
        try:
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
            self.camera_connected = True
        except Exception as e:
            os.environ["PYLON_CAMEMU"] = "4"
            self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

        return self.camera

    def set_emulated_image(self, path):
        # doesnt work
        os.environ["PYLON_CAMEMU_IMAGE"] = path

    
    def use_default_calibration(self, startup = False):
        self.mtx = self.default_mtx.copy()
        self.dist = self.default_dist.copy()
        if startup is True:
            self.camera_calibrated = False
        else:
            self.camera_calibrated = True
    
    def calibrate_camera(self):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
        objp = np.zeros((self.checkerboard_dimensions[0] * self.checkerboard_dimensions[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard_dimensions[0], 0:self.checkerboard_dimensions[1]].T.reshape(-1, 2)
        
        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        
        
        num_failed_images = 0 
        for index, image in enumerate(self.calibration_images):

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, self.checkerboard_dimensions, None)
        
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
        
                corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners2)
            else:
               num_failed_images += 1

        cv2.destroyAllWindows()

        # Check if objpoints and imgpoints are not empty
        if len(objpoints) > 0 and len(imgpoints) > 0:
            # Calibration Successful
            self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            self.set_calibration_values(self.ret, self.mtx, self.dist, self.rvecs, self.tvecs)
            return True, num_failed_images
        else:
            # Calibration failed
            self.reset_calibration()
            return False, num_failed_images
            

    def capture_image(self):
        # use default close to retain camera state outside of function
        default_closed = False

        if not self.camera.IsOpen():
            self.camera.Open()
            default_closed = True

        # Start capturing a single image
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        # Retrieve the image (blocking call)
        grabResult = self.camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

        # Convert the image to a numpy array
        image_array = grabResult.GetArray()

        # Convert image array to the desired format (e.g., uint8 or uint16, based on your camera settings)
        image_array = np.array(image_array, dtype=np.uint8)

        # Demosaic the raw Bayer image to a full-color image
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BAYER_BG2BGR)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR) # necessary?

        # Stop grabbing
        self.camera.StopGrabbing()

        #close the camera if it was closed before
        if default_closed:
            self.camera.Close()
        

        return image_array

def crop_image(image, top_left, bottom_right):

    x1, y1 = top_left
    x2, y2 = bottom_right
    image_array_image = image[y1:y2, x1:x2]
    return image_array_image




# old functions Remove later?

def save_checkerboard_images(camera_object, num_images = 1, save_dir = r'C:\Users\mtec\Desktop\Thesis_Misc_Valentin\Python_Skripts\Checkerboard_Images'):
    camera = camera_object.camera

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for i in range(num_images):
        camera.Open()
        image_array = camera_object.capture_image()
        image_array = crop_image(image_array, (600, 130), (875, 385))
        camera.Close()
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        image_path = os.path.join(save_dir, f'checkerboard_{i+1}.jpg')
        cv2.imwrite(image_path, image_array)
        print(f'Saved {image_path}')
        cv2.imshow('Checkerboard Image', image_array)
        cv2.waitKey(0)  # Display each image for 500 ms

    cv2.destroyAllWindows()

    return 0





