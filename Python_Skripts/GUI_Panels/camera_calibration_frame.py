import tkinter as tk
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from Function_Groups.camera import capture_image, crop_image


class CameraCalibrationFrame:
    def __init__(self, parent, root):
        self.checkerboard_images = []
        self.checkerboard_size = 5
        self.checkerboard_dimensions = (7,4)
        self.checkerboard_image_amount = 10


        self.camera = root.camera_object.camera
        self.log = root.log
        self.canvas = root.camera_plot_frame.canvas


        self.frame = tk.LabelFrame(parent, text="Camera Calibration", name="camera_calibration_frame")

        for i in range(6):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.frame.grid_columnconfigure(i, weight=1)

        self.frame.columnconfigure(2, weight=100)

        #TODO decide on better grid layout

        calibration_crop_top_left_label = tk.Label(self.frame, text="Top Left Corner: [x,y]", name="calibration_crop_top_left_label")
        calibration_crop_top_left_label.grid(row=0, column=0, pady=5, sticky="w")
        self.calibration_crop_top_left_entry = tk.Entry(self.frame, name="calibration_crop_top_left_entry")
        self.calibration_crop_top_left_entry.grid(row=0, column=1, pady=5)
        self.calibration_crop_top_left_entry.insert(0, "0,0")

        calibration_crop_bottom_right_label = tk.Label(self.frame, text="Bottom Right Corner: [x,y]", name="calibration_crop_bottom_right_label")
        calibration_crop_bottom_right_label.grid(row=1, column=0, pady=0, sticky="w")
        self.calibration_crop_bottom_right_entry = tk.Entry(self.frame, name="calibration_crop_bottom_right_entry")
        self.calibration_crop_bottom_right_entry.grid(row=1, column=1, pady=0)
        self.calibration_crop_bottom_right_entry.insert(0, "1920,1080")

        checkerboard_size_label = tk.Label(self.frame, text="Checkerboard Size [mm]: ", name="checkerboard_size_label")
        checkerboard_size_label.grid(row=2, column=0, pady=5, sticky="w")
        self.checkerboard_size_entry = tk.Entry(self.frame, name="checkerboard_size_entry")
        self.checkerboard_size_entry.grid(row=2, column=1, pady=5)
        self.checkerboard_size_entry.insert(0, self.checkerboard_size)

        checkerboard_corners_label = tk.Label(self.frame, text="Checkerboard Corners [x,y]: ", name="checkerboard_corners_label")
        checkerboard_corners_label.grid(row=3, column=0, pady=0, sticky="w")
        self.checkerboard_corners_entry = tk.Entry(self.frame, name="checkerboard_corners_entry")
        self.checkerboard_corners_entry.grid(row=3, column=1, pady=0)
        self.checkerboard_corners_entry.insert(0, f"{self.checkerboard_dimensions[0]},{self.checkerboard_dimensions[1]}")


        self.take_image_button = tk.Button(self.frame, command=self.take_calibration_image, text="Take Image " + str(len(self.checkerboard_images)+1)) #+ "/" + str(self.checkerboard_image_amount))
        self.take_image_button.grid(row=4, column=0,padx=10, pady=5, sticky="e")

        self.calibrate_button = tk.Button(self.frame, text="Calibrate", command=self.calibrate_camera, state="active") # TODO decide on state
        self.calibrate_button.grid(row=4, column=1, pady=5, sticky="w")

        self.reset_button = tk.Button(self.frame, text="Reset", command=self.reset_calibration)
        self.reset_button.grid(row=5, column=1, columnspan=1, pady=5, sticky="w")

    def reset_calibration(self):
        self.checkerboard_images = []
        self.update_calibration_images()
        self.take_image_button.config(text="Take Image " + str(len(self.checkerboard_images) + 1))
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = None , None, None, None , None
    
    def take_calibration_image(self):
        #if len(self.checkerboard_images) < self.checkerboard_image_amount:         
        self.camera.Open()
        image = capture_image(self.camera)
        self.camera.Close()

        # Crop the image
        top_left = tuple(map(int, self.calibration_crop_top_left_entry.get().split(',')))
        bottom_right = tuple(map(int, self.calibration_crop_bottom_right_entry.get().split(',')))
        image = crop_image(image, top_left, bottom_right)

        self.checkerboard_images.append(image)
        self.log_event("Took calibration image")

        #if len(self.checkerboard_images) > 0:
        #self.create_calibration_image_canvas(self.calibration_image_frame) #TODO uncomment if subplots dont work  

        self.update_calibration_images()

        # Update Buttons
        self.take_image_button.config(text="Take Image " + str(len(self.checkerboard_images) + 1)) #+ "/" + str(self.checkerboard_image_amount))
    
        """
        if len(self.checkerboard_images) == self.checkerboard_image_amount:
            # Update Buttons
            self.take_image_button.config(state="disabled", text="Done")
            self.calibrate_button.config(state="normal")
            self.log_event("Reached maximum amount of calibration images")
        """
   
    def update_calibration_images(self): #TODO change layout of subplots
        num_images = len(self.checkerboard_images)
        rows = 1  # subplots layout
        cols = max(num_images,1) # ensure at least one column

        fig, axs = plt.subplots(rows, cols, figsize=(8, 4 * rows))
        fig.subplots_adjust(hspace=0.2)

        if num_images == 0:
            axs = [axs]
            axs[0].axis('off')

        for i in range(num_images):
            row = i // cols 
            col = i % cols
            if cols > 1: # Handle multiple columns
                ax = axs[col]
            else:
                ax = axs if num_images == 1 else axs[col]
            ax.imshow(self.checkerboard_images[i], cmap='gray')
            ax.set_title(f"Image {i + 1}")
            ax.axis('off')

        fig.tight_layout() # Adjust the layout to rezise the subplots

        canvas = self.calibration_image_frame.canvas
        canvas.figure = fig
        canvas.draw()

        self.log_event("Updated Calibration Images")
    
    def calibrate_camera(self):
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
        
                # Draw and display the corners
                cv2.drawChessboardCorners(image, self.checkerboard_dimensions, corners2, ret)
                self.update_calibration_images()
             
            else:
                self.log_event(f"Checkerboard corners not found in image {index+1}")

        cv2.destroyAllWindows()

        # Check if objpoints and imgpoints are not empty
        if len(objpoints) > 0 and len(imgpoints) > 0:
            # Calibrate the camera
            self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

            # Update the camera calibration checkbox
            self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("camera_calibrated").select()
            self.camera_calibrated = True
            self.log_event("Calibrated Camera")
        else:
            self.log_event("Calibration failed: No valid checkerboard corners found in any image")
 
