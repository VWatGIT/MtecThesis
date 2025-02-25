import tkinter as tk
import cv2
import numpy as np
import threading

from Python_Skripts.Function_Groups.camera import crop_image
from Python_Skripts.GUI_Panels.Movement_Procedures.calibration_movement import take_calibration_images


class CameraCalibrationFrame:
    def __init__(self, parent, root):
        self.root = root
        self.checkerboard_images = self.root.camera_object.calibration_images
        self.checkerboard_size = root.checkerboard_size
        self.checkerboard_dimensions = root.checkerboard_dims
        self.checkerboard_image_amount = root.num_calibration_images

        self.camera_object = root.camera_object
        self.camera = root.camera_object.camera
        self.log = root.log
        self.canvas = root.camera_plot_frame.canvas

        # start thread with calibration button
        self.calibration_thread = threading.Thread(target=self.calibrate_camera)

        self.frame = tk.LabelFrame(parent, text="Camera Calibration", name="camera_calibration_frame")

        for i in range(5):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

       
        checkerboard_size_label = tk.Label(self.frame, text="Checkerboard Size [mm]: ", name="checkerboard_size_label")
        checkerboard_size_label.grid(row=0, column=0, pady=5, sticky="w")
        self.checkerboard_size_entry = tk.Entry(self.frame, name="checkerboard_size_entry")
        self.checkerboard_size_entry.grid(row=0, column=1, pady=5)
        self.checkerboard_size_entry.insert(0, self.checkerboard_size)

        checkerboard_corners_label = tk.Label(self.frame, text="Checkerboard Corners [x,y]: ", name="checkerboard_corners_label")
        checkerboard_corners_label.grid(row=1, column=0, pady=0, sticky="w")
        self.checkerboard_corners_entry = tk.Entry(self.frame, name="checkerboard_corners_entry")
        self.checkerboard_corners_entry.grid(row=1, column=1, pady=0)
        self.checkerboard_corners_entry.insert(0, f"{self.checkerboard_dimensions[0]},{self.checkerboard_dimensions[1]}")

        
        self.num_calibratrion_images_label = tk.Label(self.frame, text="Number of Images: ", name="num_calibratrion_images_label")
        self.num_calibratrion_images_label.grid(row=2, column=0, pady=5, sticky="w")

        self.num_calibratrion_images_slider = tk.Scale(self.frame, from_=1, to=root.max_num_calibration_images, orient="horizontal", name="num_calibratrion_images_slider", variable=self.checkerboard_image_amount)
        self.num_calibratrion_images_slider.grid(row=2, column=1,columnspan=1, pady=5, sticky="ew")

        self.use_default_calibration_button = tk.Button(self.frame, text="Use Default\nCalibration", command=self.use_default_calibration)
        self.use_default_calibration_button.grid(row=3, column=0, pady=5, sticky="e")
        
        self.calibrate_button = tk.Button(self.frame, text="Calibrate", command=self.calibration_thread.start, state="active") 
        self.calibrate_button.grid(row=3, column=1, pady=5, sticky="w")

        self.reset_button = tk.Button(self.frame, text="Reset", command=self.reset_calibration)
        self.reset_button.grid(row=4, column=1, columnspan=1, pady=5, sticky="w")

    def use_default_calibration(self):
        self.camera_object.use_default_calibration()
        self.log.log_event("Set Default Camera Calibration")


    def reset_calibration(self):
        self.camera_object.reset_calibration()
        self.log.log_event("Reset Camera Calibration")

    def calibrate_camera(self):
        # get images from different angles
        self.checkerboard_images = take_calibration_images(self.root)
        
        # now calibrate based on checkerboard images

        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
        objp = np.zeros((self.checkerboard_dimensions[0] * self.checkerboard_dimensions[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard_dimensions[0], 0:self.checkerboard_dimensions[1]].T.reshape(-1, 2)
        
        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        
        
        for index, image in enumerate(self.checkerboard_images):

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, self.checkerboard_dimensions, None)
        
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
        
                corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners2)
            else:
                self.root.log.log_event(f"Checkerboard corners not found in image {index+1}")

        cv2.destroyAllWindows()

        # Check if objpoints and imgpoints are not empty
        if len(objpoints) > 0 and len(imgpoints) > 0:
            # Calibrate the camera
            self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
            self.camera_object.set_calibration_values(self.ret, self.mtx, self.dist, self.rvecs, self.tvecs)
            self.log.log_event("Calibrated Camera")
        else:
            self.log.log_event("Calibration failed: No valid checkerboard corners found in any image")
            self.reset_calibration()
 
    def draw_calibration(self, image):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        
        # Prepare object points (0,0,0), (1,0,0), (2,0,0), ..., (6,5,0)
        objp = np.zeros((self.checkerboard_dimensions[0] * self.checkerboard_dimensions[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:self.checkerboard_dimensions[0], 0:self.checkerboard_dimensions[1]].T.reshape(-1, 2)
        
        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray, self.checkerboard_dimensions, None)
    
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
    
            corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
            imgpoints.append(corners2)
    
            # Draw and display the corners
            cv2.drawChessboardCorners(image, self.checkerboard_dimensions, corners2, ret)

        return image