import tkinter as tk
import threading
from configparser import ConfigParser
import os

from Python_Skripts.GUI_Panels.Movement_Procedures.calibration_movement import take_calibration_images


class CameraCalibrationFrame:
    def __init__(self, parent, root):
        self.root = root
        self.checkerboard_images = self.root.camera_object.calibration_images
        self.checkerboard_size = root.camera_object.checkerboard_size
        self.checkerboard_dimensions = root.camera_object.checkerboard_dimensions
        self.checkerboard_image_amount = root.camera_object.num_calibration_images

        self.camera_object = root.camera_object
        self.camera = root.camera_object.camera
        self.log = root.log
        self.canvas = root.camera_plot_frame.canvas

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

        self.num_calibratrion_images_slider = tk.Scale(self.frame, from_=1, to=root.camera_object.max_num_calibration_images, orient="horizontal", name="num_calibratrion_images_slider", variable=self.checkerboard_image_amount)
        self.num_calibratrion_images_slider.grid(row=2, column=1,columnspan=1, pady=5, sticky="ew")

        self.calibrate_button = tk.Button(self.frame, text="Calibrate", command=self.start_calibration, state="active") 
        self.calibrate_button.grid(row=3, column=1, pady=5, sticky="w")

        self.reset_button = tk.Button(self.frame, text="Reset", command=self.reset_calibration)
        self.reset_button.grid(row=3, column=0, pady=5, padx=30, sticky="e")

        self.use_default_calibration_button = tk.Button(self.frame, text="Use Default", command=self.use_default_calibration)
        self.use_default_calibration_button.grid(row=4, column=0, pady=5, padx=30, sticky="e")

        self.save_as_default_calibration_button = tk.Button(self.frame, text="Save as Default", command=self.save_as_default_calibration)
        self.save_as_default_calibration_button.grid(row=4, column=1, pady=5, sticky="w")

    
    def save_as_default_calibration(self):
        new_default_mtx = self.camera_object.mtx.copy()
        new_default_dist = self.camera_object.dist.copy()

        # Load the existing config file
        config = ConfigParser(comment_prefixes='#', allow_no_value=True)
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config.ini'))
        config.read(config_path)

        # Update the default calibration values
        config.set('Camera', 'default_mtx', ','.join(map(str, new_default_mtx.flatten())))
        config.set('Camera', 'default_dist', ','.join(map(str, new_default_dist.flatten())))

        # Read the original file lines
        with open(config_path, 'r') as file:
            lines = file.readlines()

        # Write the updated config back to the file, preserving comments 
        # configparser overwrites comments sadly by default
        # I dont have to do this often so its fine
        with open(config_path, 'w') as file:
            for line in lines:
                if line.strip().startswith('default_mtx'):
                    file.write(f"default_mtx = {', '.join(map(str, new_default_mtx.flatten()))}\n")
                elif line.strip().startswith('default_dist'):
                    file.write(f"default_dist = {', '.join(map(str, new_default_dist.flatten()))}\n")
                else:
                    file.write(line)


        self.log.log_event("Saved Camera Calibration as Default in config.ini")

    def use_default_calibration(self):
        self.camera_object.use_default_calibration()
        self.log.log_event("Set Default Camera Calibration")


    def reset_calibration(self):
        self.camera_object.reset_calibration()
        self.log.log_event("Reset Camera Calibration")

    def start_calibration(self):
        # start thread with calibration button
        calibration_thread = threading.Thread(target=self.calibrate_camera)
        calibration_thread.start()

    def calibrate_camera(self):
        # get images from different angles
        self.checkerboard_images = take_calibration_images(self.root)
        
        # now calibrate based on checkerboard images
        result, failed_images = self.camera_object.calibrate_camera()
        if result:
            
            self.log.log_event(f"Calibration successful: {(len(self.camera_object.calibration_images) - failed_images)}/{len(self.camera_object.calibration_images)} images valid")
        else:
            self.log.log_event(f"Calibration failed: 0/{len(self.camera_object.calibration_images)} images valid")

 
