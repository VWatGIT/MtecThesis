import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import pprint
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pypylon.pylon as pylon
from scipy.interpolate import griddata
from CaptureIMG import capture_image
from calibrate_camera import calibrate_camera
from Object3D import Sensor, Probe, Hexapod
from CreatePath import generate_grid, generate_snake_path
from probe_tip_detection import detect_needle_tip
from probe_tip_detection import crop_image
from probe_tip_detection import crop_coordinate_transform
from alignment import fine_alignment
from alignment import rough_alignment
from detect_markers import detect_markers

import os
import h5py
import time
from datetime import datetime

class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Probe Beam Measurement")
        self.root.geometry("1600x1000")

        self.tab_count = 0
        #self.tabs = {}

        self.data = {} # Data dictionary

        #implement support for multiple data tabs
        
        self.sensor = Sensor()
        self.probe = Probe()
        self.hexapod = Hexapod()

        # Default values
        self.grid_size = (1, 1, 1) #mm

        self.step_size = 1 #mm
        self.measurement_points = 1
        self.time_estimated = 0
        self.elapsed_time = 0

        self.current_measurement_id = 0
        
        # TODO make callback function for values changed in entry fields

        os.environ["PYLON_CAMEMU"] = "1" # Enable the pylon camera emulator
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = None , None, None, None , None # Camera Calibration Values

        self.checkerboard_images = []
        self.checkerboard_image_amount = 3
        self.checkerboard_dimensions = (7,4)
        self.checkerboard_size = 5 #mm size of one square edge TODO change dafault value

        self.detected_probe_position = None

        # Create the GUI
        self.create_menu()
        self.create_left_panel() # includes home, new_measurement, load_measurement
        self.create_paned_window() # also creates tab_group and event_log_panel and camera_panel 
        self.show_home_panel()
        self.show_camera_panel()
   

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        menubar.add_command(label="Home", command=self.show_home_panel)
        menubar.add_command(label="New", command=self.show_new_measurement_panel)
        menubar.add_command(label="Load", command=self.show_load_measurement_panel)
        menubar.add_command(label="Camera", command=self.show_camera_panel)
        menubar.add_command(label="Help", command=self.show_help_panel)

    def create_left_panel(self):
        self.left_panel = tk.Frame(self.root, width=340) # TODO change this depending on needed menu size
        self.left_panel.pack(side="left", fill="both")

        self.create_home_panel(self.left_panel)
        self.create_new_measurement_panel(self.left_panel)
        self.create_load_measurement_panel(self.left_panel)
    def create_home_panel(self, parent):
        self.home_panel = tk.Frame(parent)

        button_width = 20  # Adjust the width as needed
        button_height = 3  # Adjust the height as needed
        button_padx = 0  # Adjust the horizontal padding as needed
        button_pady = 40  # Adjust the vertical padding as needed

        new_measurement_button = tk.Button(self.home_panel, text="New Measurement", command=self.show_new_measurement_panel, width=button_width, height=button_height)
        new_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)

        load_measurement_button = tk.Button(self.home_panel, text="Load Measurement", command=self.show_load_measurement_panel, width=button_width, height=button_height)
        load_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)

        camera_button = tk.Button(self.home_panel, text="Camera", command=self.show_camera_panel, width=button_width, height=button_height)
        camera_button.pack(side="top", padx=button_padx, pady=button_pady)

        help_button = tk.Button(self.home_panel, text="Help", command=self.show_help_panel, width=button_width, height=button_height)
        help_button.pack(side="top", padx=button_padx, pady=button_pady)
    def create_new_measurement_panel(self, parent):
        self.new_measurement_panel = tk.Frame(parent)

        # Create grid 
        for i in range(10):
            self.new_measurement_panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.new_measurement_panel.grid_columnconfigure(i, weight=1)

        input_frame = tk.LabelFrame(self.new_measurement_panel,text ="New Measurement",name="input_frame")
        input_frame.grid(row=0, column=0, rowspan=2, columnspan=2, sticky="nsew", padx=10, pady=10) 

        for i in range(3):
            input_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            input_frame.grid_columnconfigure(i, weight=1)

        probe_name_label = tk.Label(input_frame, text="Probe Name:")
        probe_name_label.grid(row=0, column=0, pady=5, sticky="e")
        self.probe_name_entry = tk.Entry(input_frame, name="probe_name_entry")
        self.probe_name_entry.grid(row=0, column=1, pady=5, sticky = "w")
        self.probe_name_entry.insert(0, "Default")

        # TODO maybe add aditional input fields for new measurement

        measurement_space_label = tk.Label(input_frame, text="3D Size:")
        measurement_space_label.grid(row=1, column=0, pady=5, sticky="e")
        self.measurement_space_entry = tk.Entry(input_frame, name = "measurement_space_entry")
        self.measurement_space_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.measurement_space_entry.insert(0, f"{self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]}")
        #TODO extract values from entry field with , seperator

        #Set up inputs for Step Size
        step_size_label = tk.Label(input_frame, text="Step Size:")
        step_size_label.grid(row=2, column=0, pady=5, sticky="e")
        self.step_size_entry = tk.Entry(input_frame, name = "step_size_entry")
        self.step_size_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.step_size_entry.insert(0, self.step_size)

        #Set up checkboxes
        checkbox_panel = tk.Frame(self.new_measurement_panel, name="checkbox_panel")
        checkbox_panel.grid(row=2, column=0, columnspan=2, padx= 10, pady=5, sticky="nsew")

        for i in range(7):
            checkbox_panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            checkbox_panel.grid_columnconfigure(i, weight=1)

        camera_connected = tk.Checkbutton(checkbox_panel, text="Camera connected", name="camera_connected", state="disabled")
        camera_connected.grid(row=0, column=0, pady=5, sticky="w")
        camera_connected.select() # TODO iplement camera connection status somewhere else

        open_camera_button = tk.Button(checkbox_panel, text="Open Camera", command=self.show_camera_panel)
        open_camera_button.grid(row=0, column=1, pady=5, sticky="w")

        camera_calibrated = tk.Checkbutton(checkbox_panel, text="Camera calibrated", name="camera_calibrated", state="disabled") 
        camera_calibrated.grid(row=1, column=0, pady=5, sticky="w")

        sensor_detected = tk.Checkbutton(checkbox_panel, text="Sensor detected", name="markers_detected", state="disabled")
        sensor_detected.grid(row=2, column=0, pady=5, sticky="w")

        probe_detected = tk.Checkbutton(checkbox_panel, text="Probe detected", name="probe_detected", state="disabled")
        probe_detected.grid(row=3, column=0, pady=5, sticky="w")

        hexapod_connected = tk.Checkbutton(checkbox_panel, text="Hexapod connected", name="hexapod_connected", state="disabled")
        hexapod_connected.grid(row=4, column=0, pady=5, sticky="w")

        connection_frame = tk.LabelFrame(checkbox_panel, name="connection_frame")
        connection_frame.grid(row=1, column=1, rowspan=4 , sticky="nsew")

        for i in range(3):
            connection_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            connection_frame.grid_columnconfigure(i, weight=1)
        
        port_1_label = tk.Label(connection_frame, text="Port 1:")
        port_1_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.port_1_entry = tk.Entry(connection_frame, name="port_1_entry")
        self.port_1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.port_1_entry.insert(0, "5464")

        port_2_label = tk.Label(connection_frame, text="Port 2:")
        port_2_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.port_2_entry = tk.Entry(connection_frame,name = "port_2_entry")
        self.port_2_entry.grid(row=1, column=1, padx=5, pady=5)
        self.port_2_entry.insert(0, "5465")

        ip_label = tk.Label(connection_frame, text="IP:")
        ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.ip_entry = tk.Entry(connection_frame, name="ip_entry")
        self.ip_entry.grid(row=2, column=1, padx=5, pady=5)
        self.ip_entry.insert(0, '134.28.45.71') # TODO change to default value

        connect_hexapod_button = tk.Button(connection_frame, text="Connect Hexapod", command=self.connect_hexapod)
        connect_hexapod_button.grid(row=3, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")

        rough_alignment = tk.Checkbutton(checkbox_panel, text="Rough Alignment", name="rough_alignment", state="disabled")
        rough_alignment.grid(row=5, column=0, pady=5, sticky="w")

        rough_alignment_button = tk.Button(checkbox_panel, text="Rough Align", command=self.rough_alignment)
        rough_alignment_button.grid(row=5, column=1, pady=5, sticky="w")

        fine_alignment = tk.Checkbutton(checkbox_panel, text="Fine Alignment", name="fine_alignment", state="disabled") # gets enabled after rough alignment
        fine_alignment.grid(row=6, column=0, pady=5, sticky="w") 

        fine_alignment_button = tk.Button(checkbox_panel, text="Fine Align", command=self.fine_alignment)
        fine_alignment_button.grid(row=6, column=1, pady=5, sticky="w")

        time_estimated_label = tk.Label(checkbox_panel, text="Estimated Time: N/A ", name="time_estimated_label") # TODO implement time estimation
        time_estimated_label.grid(row=7, column=0, pady=5, sticky="w")

        time_estimation_button = tk.Button(checkbox_panel, text="Estimate Time", command=self.estimate_time)
        time_estimation_button.grid(row=7, column=1, pady=5, sticky="w")


        progress_bar = ttk.Progressbar(self.new_measurement_panel, orient="horizontal", length=320, mode="determinate", name="progress_bar")
        progress_bar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        #Set up Big Buttons
        start_button = tk.Button(self.new_measurement_panel, text="START", name="start_button", command=self.start_button_pushed, width = 20, height = 3)
        start_button.grid(row=4, column=0, padx=10, pady=5, sticky = "w")

        save_button = tk.Button(self.new_measurement_panel, text="SAVE",name="save_button", command=self.save_button_pushed, width = 20, height =3, state="disabled")
        save_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")

    def create_load_measurement_panel(self, parent):
        self.load_measurement_panel = tk.Frame(parent)

        load_button = tk.Button(self.load_measurement_panel, text="LOAD", command=self.load_button_pushed, width=20, height=3)
        load_button.pack(pady=30)

        return_button = tk.Button(self.load_measurement_panel, text="Return", command=self.show_home_panel, width=20, height=3)
        return_button.pack(pady=30)
    def create_camera_panel(self, parent):
        self.camera_panel = tk.LabelFrame(parent, name="camera_panel")
        self.camera_panel.place(relx=1, rely=1, anchor="center", relheight=1, relwidth=1)

        for i in range(2):
            self.camera_panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.camera_panel.grid_columnconfigure(i, weight=1)

        self.create_camera_plot_frame(self.camera_panel)
        self.create_camera_settings_frame(self.camera_panel)
        self.create_camera_calibration_frame(self.camera_panel)
        self.create_camera_detection_frame(self.camera_panel)

        self.camera_plot_frame = self.camera_panel.nametowidget("camera_plot_frame")
        self.camera_plot_frame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)
        
        self.camera_settings_frame = self.camera_panel.nametowidget("camera_settings_frame")
        self.camera_settings_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10) 

        self.camera_calibration_frame = self.camera_panel.nametowidget("camera_calibration_frame")
        self.camera_calibration_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.camera_detection_frame = self.camera_panel.nametowidget("camera_detection_frame")
        self.camera_detection_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        return_button = tk.Button(self.camera_panel, text="Return", command= lambda: self.camera_panel.place_forget())
        return_button.place(relx=1, rely= 0, anchor="ne")
    def create_help_panel(self, parent):
        self.help_panel = tk.Frame(parent, name="help_panel")
        help_text = "This is a help text."
        help_label = tk.Label(self.help_panel, text=help_text)

    def show_home_panel(self):
        self.hide_all_panels()
        self.home_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_new_measurement_panel(self):
        self.hide_all_panels()
        self.new_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_load_measurement_panel(self):
        self.hide_all_panels()
        self.load_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_camera_panel(self):
        if not self.camera_panel:
            self.create_camera_panel()
        self.camera_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_help_panel(self):
            if not self.camera_panel:
                self.create_help_panel()
            self.help_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def hide_all_panels(self):
        self.home_panel.place_forget()
        self.new_measurement_panel.place_forget()
        self.load_measurement_panel.place_forget()
        self.camera_panel.place_forget()
        self.help_panel.place_forget()

    def create_camera_plot_frame(self, parent):
        self.camera_plot_frame = tk.LabelFrame(parent, text="Camera Image", name="camera_plot_frame")
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=self.camera_plot_frame)
        canvas.get_tk_widget().place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
        self.camera_plot_frame.canvas = canvas
        ax.axis('off')
    def create_camera_settings_frame(self, parent):
        self.camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        toggle_camera_button = tk.Checkbutton(self.camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera)
        toggle_camera_button.pack(side = "top", pady=5)
    def create_camera_detection_frame(self, parent):
        camera_detection_frame = tk.LabelFrame(parent, text="Detection", name="camera_detection_frame")

        self.create_probe_detection_frame(camera_detection_frame)
        self.probe_detection_frame = camera_detection_frame.nametowidget("probe_detection_frame")
        self.probe_detection_frame.pack(side = "left", fill="both", expand=True)

        self.create_marker_detection_frame(camera_detection_frame)
        self.marker_detection_frame = camera_detection_frame.nametowidget("marker_detection_frame")
        self.marker_detection_frame.pack(side = "right", fill="both", expand=True)

    def create_probe_detection_frame(self, parent):
        probe_detection_frame = tk.LabelFrame(parent, text="Probe Tip", name="probe_detection_frame")
        
        for i in range(1):
            probe_detection_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            probe_detection_frame.grid_columnconfigure(i, weight=1)

        self.create_probe_detection_input_frame(probe_detection_frame)
        
        self.probe_detection_input_frame = probe_detection_frame.nametowidget("probe_detection_input_frame")
        self.probe_detection_input_frame.grid(row=0, column=0, pady=5, sticky = "n")

        # Create a frame for the probe plot
        self.probe_plot_frame = tk.Frame(probe_detection_frame, name="probe_plot_frame")
        self.probe_plot_frame.grid(row=0, column=1, pady=5, sticky = "nsew")

        fig, ax = plt.subplots() # Maybe use multiple subplots
        canvas = FigureCanvasTkAgg(fig, master=self.probe_plot_frame)
        canvas.get_tk_widget().pack(side="left", fill="both")
        self.probe_plot_frame.canvas = canvas
        ax.axis('off')
    def create_probe_detection_input_frame(self, parent):
        probe_detection_input_frame = tk.Frame(parent, name="probe_detection_input_frame")

        
        for i in range(5):
            probe_detection_input_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            probe_detection_input_frame.grid_columnconfigure(i, weight=1)


        self.crop_top_left_label = tk.Label(probe_detection_input_frame, text="Top Left Corner: [x,y]", name="crop_top_left_label")
        self.crop_top_left_label.grid(row=0, column=0, pady=5)
        self.crop_top_left_entry = tk.Entry(probe_detection_input_frame, name="crop_top_left_entry")
        self.crop_top_left_entry.grid(row=0, column=1, pady=5)
        self.crop_top_left_entry.insert(0, "0,0")

        self.crop_bottom_right_label = tk.Label(probe_detection_input_frame, text="Bottom Right Corner: [x,y]", name="crop_bottom_right_label")
        self.crop_bottom_right_label.grid(row=1, column=0, pady=5)
        self.crop_bottom_right_entry = tk.Entry(probe_detection_input_frame, name="crop_bottom_right_entry")
        self.crop_bottom_right_entry.grid(row=1, column=1, pady=5)
        self.crop_bottom_right_entry.insert(0, "1920,1080")

        self.threshold_slider_label = tk.Label(probe_detection_input_frame, text="Threshold Value", name="threshold_slider_label") 
        self.threshold_slider_label.grid(row=2, column=0, rowspan=2, pady=5)
        self.threshold_slider = tk.Scale(probe_detection_input_frame, from_=0, to=255, orient="horizontal", name="threshold_slider")
        self.threshold_slider.grid(row=2, column=1, rowspan=2, pady=5)


        self.take_probe_image_button = tk.Button(probe_detection_input_frame, text="Take Image", command=self.take_probe_image) # TODO implement crop_image
        self.take_probe_image_button.grid(row=4, column=0, columnspan=2,rowspan = 2,pady=5)

        probe_detection_input_frame.grid_rowconfigure(3, weight=3) #weight row for gap
        
        self.save_probe_position_button = tk.Button(probe_detection_input_frame, text="Save Position", command=self.save_probe_position, state="disabled") # TODO implement detect_probe
        self.save_probe_position_button.grid(row=6, column=1, pady=5)

        self.probe_detetection_checkbox = tk.Checkbutton(probe_detection_input_frame, text="Probe Detected", name="probe_detected", state="disabled")
        self.probe_detetection_checkbox.grid(row=6, column=0, pady=5)
    def create_marker_detection_frame(self, parent):
        marker_detection_frame = tk.LabelFrame(parent, text="Marker Detection", name="marker_detection_frame")
        # TODO implement marker detection

    def scan_markers(self, image):
        image = rvecs, tvecs = detect_markers(image, self.mtx, self.dist)

        self.sensor.marker_rvecs = rvecs[self.sensor.marker_id]
        self.sensor.marker_tvecs = tvecs[self.sensor.marker_id]

        self.probe.marker_rvecs = rvecs[self.probe.marker_id]
        self.probe.marker_tvecs = tvecs[self.probe.marker_id]

        self.update_marker_plot(image)

    def update_marker_plot(self, image):
        # TODO implement marker detection plot
        pass



    def create_camera_calibration_frame(self, parent):

        self.camera_calibration_frame = tk.LabelFrame(parent, text="Camera Calibration", name="camera_calibration_frame")

        for i in range(6):
            self.camera_calibration_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.camera_calibration_frame.grid_columnconfigure(i, weight=1)

        self.create_calibration_image_frame(self.camera_calibration_frame)

        self.calibration_image_frame = self.camera_calibration_frame.nametowidget("calibration_image_frame")
        self.calibration_image_frame.grid(row=0, column=2, rowspan=6, columnspan=2, pady=5, sticky="nsew") # why rowspan 6?
        self.calibration_image_frame.propagate(False)
        self.camera_calibration_frame.columnconfigure(2, weight=100)

        #TODO decide on better grid layout

        calibration_crop_top_left_label = tk.Label(self.camera_calibration_frame, text="Top Left Corner: [x,y]", name="calibration_crop_top_left_label")
        calibration_crop_top_left_label.grid(row=0, column=0, pady=5, sticky="w")
        self.calibration_crop_top_left_entry = tk.Entry(self.camera_calibration_frame, name="calibration_crop_top_left_entry")
        self.calibration_crop_top_left_entry.grid(row=0, column=1, pady=5)
        self.calibration_crop_top_left_entry.insert(0, "0,0")

        calibration_crop_bottom_right_label = tk.Label(self.camera_calibration_frame, text="Bottom Right Corner: [x,y]", name="calibration_crop_bottom_right_label")
        calibration_crop_bottom_right_label.grid(row=1, column=0, pady=0, sticky="w")
        self.calibration_crop_bottom_right_entry = tk.Entry(self.camera_calibration_frame, name="calibration_crop_bottom_right_entry")
        self.calibration_crop_bottom_right_entry.grid(row=1, column=1, pady=0)
        self.calibration_crop_bottom_right_entry.insert(0, "1920,1080")

        checkerboard_size_label = tk.Label(self.camera_calibration_frame, text="Checkerboard Size [mm]: ", name="checkerboard_size_label")
        checkerboard_size_label.grid(row=2, column=0, pady=5, sticky="w")
        self.checkerboard_size_entry = tk.Entry(self.camera_calibration_frame, name="checkerboard_size_entry")
        self.checkerboard_size_entry.grid(row=2, column=1, pady=5)
        self.checkerboard_size_entry.insert(0, self.checkerboard_size)

        checkerboard_corners_label = tk.Label(self.camera_calibration_frame, text="Checkerboard Corners [x,y]: ", name="checkerboard_corners_label")
        checkerboard_corners_label.grid(row=3, column=0, pady=0, sticky="w")
        self.checkerboard_corners_entry = tk.Entry(self.camera_calibration_frame, name="checkerboard_corners_entry")
        self.checkerboard_corners_entry.grid(row=3, column=1, pady=0)
        self.checkerboard_corners_entry.insert(0, f"{self.checkerboard_dimensions[0]},{self.checkerboard_dimensions[1]}")


        self.take_image_button = tk.Button(self.camera_calibration_frame, command=self.take_calibration_image, text="Take Image " + str(len(self.checkerboard_images)+1)) #+ "/" + str(self.checkerboard_image_amount))
        self.take_image_button.grid(row=4, column=0,padx=10, pady=5, sticky="e")

        self.calibrate_button = tk.Button(self.camera_calibration_frame, text="Calibrate", command=self.calibrate_camera, state="active") # TODO decide on state
        self.calibrate_button.grid(row=4, column=1, pady=5, sticky="w")

        self.reset_button = tk.Button(self.camera_calibration_frame, text="Reset", command=self.reset_calibration)
        self.reset_button.grid(row=5, column=1, columnspan=1, pady=5, sticky="w")
    def create_calibration_image_frame(self, parent):
        self.calibration_image_frame = tk.LabelFrame(parent, text="Calibration Images", name="calibration_image_frame")
        
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=self.calibration_image_frame)
        canvas.get_tk_widget().pack(side="right", fill="both", expand=True) # TODO change layout
        self.calibration_image_frame.canvas = canvas
        ax.axis('off')
        fig.tight_layout()

        # Create initial Default Canvas
        #self.create_calibration_image_canvas(self.calibration_image_frame)
        #self.default_image_frame = self.calibration_image_frame.nametowidget("new_image_frame_"+ str(len(self.checkerboard_images)))

    def take_probe_image(self):
        # updates the canvas with the detected image
        # TODO access the entries in a different way, not by .self
        top_left = tuple(map(int, self.crop_top_left_entry.get().split(',')))
        bottom_right = tuple(map(int, self.crop_bottom_right_entry.get().split(',')))

        self.camera.Open()
        image = capture_image(self.camera)
        self.camera.Close()

        image = crop_image(image, top_left, bottom_right)

        # Detect the needle tip
        threshold = self.threshold_slider.get()
        result_image, detected_probe_position_cropped, pixel_size = detect_needle_tip(image, threshold) # TODO add probe rotation detection

        # translate the cropped coordinates to the original image
        
        if detected_probe_position_cropped is not None:
            self.detected_probe_position = crop_coordinate_transform(image, detected_probe_position_cropped, top_left)
            self.log_event(f"Probe-Tip detected at {self.detected_probe_position}")
            self.save_probe_position_button.config(state="normal")
            self.probe_detetection_checkbox.config(state="normal")
        else:
            self.detected_probe_position = None
            self.save_probe_position_button.config(state="disabled")
            self.probe_detetection_checkbox.config(state="disabled")
            self.log_event("Probe-Tip not detected")


        # Show the result
        canvas = self.probe_plot_frame.canvas
        axes = self.probe_plot_frame.canvas.figure.axes[0]
        axes.clear()
        axes.imshow(result_image) # Show image with detected tip drawn
        canvas.draw()
        axes.axis('off')

        self.log_event("Took Probe Image")
    def save_probe_position(self):
        # TODO maybe merge this with take probe image

        self.probe_detected = True
        self.probe_detetection_checkbox.select()

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("probe_detected").select()
        self.probe.translate_probe_tip(self.detected_probe_position, self.mtx, self.dist)
        self.log_event("Saved Probe Position")


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
            self.log_event("Calibrated Camera")
        else:
            self.log_event("Calibration failed: No valid checkerboard corners found in any image")
    def update_camera(self):    
        if self.camera.IsOpen():
            image = capture_image(self.camera)

            # Update Camera Image
            canvas = self.camera_plot_frame.canvas 
            ax = canvas.figure.axes[0]
            
            ax.clear()
            ax.imshow(image)
            canvas.draw()
            #self.root.after(10, self.update_camera()) #TODO fix bug that crashes UI
    def toggle_camera(self):
        if self.camera.IsOpen():
            self.camera.Close()
        else:
            self.camera.Open()
            self.root.after(10, self.update_camera)
        self.log_event("Toggled Camera")

    def create_paned_window(self):
        self.paned_window = ttk.PanedWindow(self.root, orient="vertical")
        self.paned_window.pack(side="right", fill="both", expand=True)

        self.helper_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.helper_frame, weight=1)

        self.create_event_log_panel(self.paned_window)

        self.create_tab_group(self.helper_frame)
        self.create_help_panel(self.helper_frame)
        self.create_camera_panel(self.helper_frame)
        
        
        self.paned_window.add(self.event_log_panel, weight=1)

        self.root.after(200, lambda: self.paned_window.sashpos(0, 840)) # set initial position of sash, after for short delay (bugfix)
        
        self.update_log()
        
    def create_tab_group(self, parent):
        self.tab_group = ttk.Notebook(parent, name="tab_group")
        self.tab_group.pack(side="right", fill="both", expand=True)

        self.create_tab() # Create the Default Tab
    def create_tab(self):
        self.tab_count += 1
        new_tab = ttk.Frame(self.tab_group, name=f"tab{self.tab_count}") # TODO change naming sceheme with probe names
        self.tab_group.add(new_tab, text=f'Tab {self.tab_count}')
        #self.tabs[self.tab_count] = new_tab

        # Configure the grid layout within the new_tab
        for i in range(2):
            new_tab.grid_columnconfigure(i, weight=1)
        for i in range(1):
            new_tab.grid_rowconfigure(i, weight=1)

        new_tab.grid_columnconfigure(1, weight=10)


        self.create_sensor_info_frame(new_tab)
        self.create_results_frame(new_tab)

        sensor_info_frame = new_tab.nametowidget("sensor_info_frame")
        sensor_info_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        results_frame = new_tab.nametowidget("results_frame")
        results_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        close_button = tk.Button(new_tab, text="Close Tab", command=lambda: self.close_tab(new_tab), name="close_button") # create this last in create_tab
        close_button.place(relx=1, rely=0, anchor="ne")  # Place the close button in the top-right corner

        self.tab_group.select(new_tab)

        # Log the creation of a new tab
        self.log_event(f"Created Tab {self.tab_count}") 
    def close_tab(self, tab):
        self.tab_group.forget(tab)
        self.log_event("Closed Tab") 
    
    def create_event_log_panel(self, paned_window):
        self.event_log_panel = tk.LabelFrame(paned_window, text="Event Log")
        self.event_log_panel.pack(side="right", fill="x", padx=10, pady=10)

        self.event_log = tk.Text(self.event_log_panel, height = 5, width = 20, state='disabled')
        self.event_log.pack(expand =True, fill="both", padx=10, pady=10)
    def log_event(self, message):
        current_time = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{current_time}] {message}"
        self.event_log.config(state='normal')
        self.event_log.insert(tk.END, formatted_message + '\n')
        self.event_log.config(state='disabled')
        self.event_log.see(tk.END)
    def update_log(self):
        #self.log_event(f"Current sash position: {self.paned_window.sashpos(0)}")
        #self.log_event(f"Number of Checkerboard Images: {len(self.checkerboard_images)}")

        self.root.after(3000, self.update_log)  # Schedule the update function to run every 5 seconds

    def create_sensor_info_frame(self, parent):
        # Create the main sensor_info_frame LabelFrame
        sensor_info_frame = tk.LabelFrame(parent, text="Measurement N/A" , name="sensor_info_frame", width=500, height=500)
    
        # Configure the grid layout within the sensor_info_frame LabelFrame
        for i in range(2):
            sensor_info_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            sensor_info_frame.grid_rowconfigure(i, weight=1)

        self.create_sensor_readings_frame(sensor_info_frame)
        #self.create_sensor_position_frame(sensor_info_frame)
        self.create_measurement_info_frame(sensor_info_frame)
        self.create_sensor_plot_frame(sensor_info_frame)

        measurment_slider = tk.Scale(sensor_info_frame, from_=1, to=100, orient="horizontal", name="measurement_slider")
        measurment_slider.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        sensor_info_frame.grid_rowconfigure(1, weight=10)

        measurment_slider.set(1)
        measurment_slider.config(resolution=1, state="normal")
        measurment_slider.bind("<ButtonRelease-1>", self.update_tab)

        

        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")
        sensor_readings_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        measurement_info_frame = sensor_info_frame.nametowidget("measurement_info_frame")
        measurement_info_frame.grid(row=1, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)

        #sensor_position_frame = sensor_info_frame.nametowidget("sensor_position_frame")
        #sensor_position_frame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)    
    
        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        sensor_plot_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)      
    def create_sensor_readings_frame(self, parent):    

        # Create a LabelFrame for X and Y positions
        sensor_readings_frame = tk.LabelFrame(parent, text="Sensor Readings", name="sensor_readings_frame")
        sensor_readings_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        for i in range(5):
            sensor_readings_frame.grid_rowconfigure(i, weight=1)

        # Add labels to display X and Y positions within the sensor_readings_frame
        xpos_label = ttk.Label(sensor_readings_frame, text="X Position: N/A", name="xpos_label")
        xpos_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ypos_label = ttk.Label(sensor_readings_frame, text="Y Position: N/A", name="ypos_label")
        ypos_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        sum_label = ttk.Label(sensor_readings_frame, text="Sum: N/A", name="sum_label")
        sum_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)

        xdiff_label = ttk.Label(sensor_readings_frame, text="X Diff: N/A", name="xdiff_label")
        xdiff_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        ydiff_label = ttk.Label(sensor_readings_frame, text="Y Diff: N/A", name="ydiff_label")
        ydiff_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)


    def create_sensor_position_frame(self, parent):    
        # Sensor Position Panel
        sensor_position_frame = tk.LabelFrame(parent, text="Sensor Position", name="sensor_position_frame")

        # Configure the grid layout within the sensor_position_frame 
        for i in range(1):
            sensor_position_frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            sensor_position_frame.grid_rowconfigure(i, weight=1)

        sensor_position_x_label = ttk.Label(sensor_position_frame, text="X Position: N/A", name="sensor_position_x_label")
        sensor_position_x_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        sensor_position_y_label = ttk.Label(sensor_position_frame, text="Y Position: N/A", name="sensor_position_y_label")
        sensor_position_y_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        sensor_position_z_label = ttk.Label(sensor_position_frame, text="Z Position: N/A", name="sensor_position_z_label")
        sensor_position_z_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        sensor_rotation_label = ttk.Label(sensor_position_frame, text="Rotation: N/A", name="sensor_rotation_label")
        sensor_rotation_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        sensor_distance_to_probe_label = ttk.Label(sensor_position_frame, text="Distance to Probe: N/A", name="sensor_distance_to_probe_label")
        sensor_distance_to_probe_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)    
    def create_sensor_plot_frame(self, parent):
        # Create a plotframe for the sensor plot
        sensor_plot_frame = tk.LabelFrame(parent, text="Detected Laser Position", name="sensor_plot_frame")
        
        # display the sensor data in a plot
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=sensor_plot_frame) 
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)  # Span the canvas across all columns
        sensor_plot_frame.canvas = canvas # store canvas in sensor_plot_frame
    def create_results_frame(self, parent):
        results_frame = tk.LabelFrame(parent, text="Results", name="results_frame")

        for i in range(2):
            results_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            results_frame.grid_rowconfigure(i, weight=1)
        

        self.create_slice_plot_frame(results_frame)
        self.create_measurement_info_frame(results_frame) # TODO put this into Sensor Info Frame

        slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
        slice_plot_frame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)

        self.create_path_plot_frame(results_frame) 
        path_plot_frame = results_frame.nametowidget("path_plot_frame")
        path_plot_frame.grid(row=1, column=1, rowspan=1, sticky="nsew", padx=10, pady=10)
    def create_slice_plot_frame(self, parent):
        slice_plot_frame = tk.LabelFrame(parent, text="Slice", name="slice_plot_frame")
        for i in range(4):
            slice_plot_frame.grid_rowconfigure(i, weight=1)
        for i in range(2): 
            slice_plot_frame.grid_columnconfigure(i, weight=1)
        
        plot_frame = tk.LabelFrame(slice_plot_frame, name="plot_frame")
        plot_frame.grid(row=0, column=0, rowspan=1, columnspan=2, sticky="nsew", padx=5, pady=5,)
        slice_plot_frame.grid_rowconfigure(0, weight=100)
        #slice_plot_frame.grid_rowconfigure(1, weight=5)
        # Create a canvas for the slice plot
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)  # Span the canvas across all columns
        plot_frame.canvas = canvas
        
        # Create Labels for the Sliders
        slice_slider_label = ttk.Label(slice_plot_frame, text="Slice Index:", name="slice_slider_label")
        slice_slider_label.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)

        contour_levels_slider_label = ttk.Label(slice_plot_frame, text="Contour Levels:", name="contour_levels_slider_label")
        contour_levels_slider_label.grid(row=1, column=1, rowspan = 1, columnspan=1, sticky="w", padx=5)

        # Create a slider for the slice plot
        slice_slider = tk.Scale(slice_plot_frame, from_=1, to=2, orient="horizontal", name="slice_slider")
        slice_slider.grid(row=2, column=0, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        slice_slider.set(1) # set default value
        slice_slider.config(resolution=1) # set slider resolution

        contour_levels_slider = tk.Scale(slice_plot_frame, from_=1, to=30, orient="horizontal", name="contour_levels_slider")
        contour_levels_slider.grid(row=2, column=1, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        contour_levels_slider.set(10) # set default value
        contour_levels_slider.config(resolution=1)

        # Create a checkbox for the slice plot
        interpolation_var = tk.IntVar()
        interpolation_checkbox = tk.Checkbutton(slice_plot_frame, text="Interpolation", name="interpolation_checkbox", variable=interpolation_var)
        interpolation_checkbox.grid(row=3, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        interpolation_checkbox.value = interpolation_var

        # trying to fix the slider bug
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        self.data["Slices"] = {} 

        slice_slider.config(command=self.update_slice_plot)
        contour_levels_slider.config(command=self.update_slice_plot)
        interpolation_checkbox.config(command=self.update_slice_plot) 

    def create_measurement_info_frame(self, parent):
        measurement_info_frame = tk.LabelFrame(parent, text="Info", name="measurement_info_frame") 

        # Configure the grid layout within the sensor_info_frame LabelFrame
        for i in range(1):
            measurement_info_frame.grid_columnconfigure(i, weight=1)
        for i in range(7):
            measurement_info_frame.grid_rowconfigure(i, weight=1)

        

        measurement_points_label = ttk.Label(measurement_info_frame, text="Measurement Points: N/A" ,name="measurement_points_label")
        measurement_points_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        slices_label = ttk.Label(measurement_info_frame, text="Slices: N/A", name="slices_label")
        slices_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        grid_size_label = ttk.Label(measurement_info_frame, text="Grid Size = N/A", name="grid_size_label")
        grid_size_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        step_size_label = ttk.Label(measurement_info_frame, text="Step Size = N/A", name="step_size_label")
        step_size_label.grid(row=3, column=0, sticky="w", padx=10, pady=5)

        time_elapsed_label = ttk.Label(measurement_info_frame, text="Time Elapsed = N/A", name="time_elapsed_label")
        time_elapsed_label.grid(row=4, column=0, sticky="w", padx=10, pady=5)
    
        time_estimated_label = ttk.Label(measurement_info_frame, text="Time Estimated = N/A", name="time_estimated_label")
        time_estimated_label.grid(row=5, column=0, sticky="w", padx=10, pady=5)    
    def create_path_plot_frame(self, parent):
        path_plot_frame = tk.LabelFrame(parent, text="Path", name="path_plot_frame")
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        canvas = FigureCanvasTkAgg(fig, master=path_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        path_plot_frame.canvas = canvas
        
        grid_size = [2, 2, 2]  # [mm] # TODO change to refer to UI parameters
        step_size = 1  # [mm]

        X, Y, Z = generate_grid(grid_size, step_size) # Create default grid

        # Plot the meshgrid points
        X_flat = X.flatten()
        Y_flat = Y.flatten()
        Z_flat = Z.flatten()

        ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.legend()
        ax.grid(True)

    # Update Functions
    def update_tab(self, event=None):    # TODO implement data input parameter
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        measurement_slider = tab.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
        self.current_measurement_id = str(measurement_slider.get())# Get the current measurement id from the slider
        self.log_event(f"Current Measurement ID: {self.current_measurement_id}")
        #self.current_measurement_id = str(int(self.measurement_spinner.get()))

        if tab:
            self.update_measurement_info_frame(tab, self.data)
            self.update_sensor_info_frame(tab, self.data)

            if self.data["Slices"] != {}:
                self.update_slice_plot()

        sensor_info_frame = tab.nametowidget("sensor_info_frame")
        sensor_info_frame.config(text="Measurement " + str(self.current_measurement_id) + "/" + str(self.measurement_points)) # Update the title



        self.log_event("Updated Tab: " + str(tab_name))
    def update_measurement_info_frame(self, tab, data):
        
        # update labels here
        

        sensor_info_frame = tab.nametowidget("sensor_info_frame")
        measurement_info_frame = sensor_info_frame.nametowidget("measurement_info_frame")
        measurement_points_label = measurement_info_frame.nametowidget("measurement_points_label")
        step_size_label = measurement_info_frame.nametowidget("step_size_label")
        time_elapsed_label = measurement_info_frame.nametowidget("time_elapsed_label")
        time_estimated_label = measurement_info_frame.nametowidget("time_estimated_label")

        measurement_points_label.config(text=f"Measurement Points: {data['3D']['measurement_points']}")
        step_size_label.config(text=f"Step Size: {data['3D']['step_size']}")
        time_elapsed_label.config(text=f"Time Elapsed: {data['info']['elapsed_time']}")
        time_estimated_label.config(text=f"Time Estimated: {data['info']['time_estimated']}")

        # update path plot here
        results_frame = tab.nametowidget("results_frame")
        path_plot_frame = results_frame.nametowidget("path_plot_frame")
        canvas = path_plot_frame.canvas
        ax = canvas.figure.axes[0]
        ax.clear() # TODO implement path plot

        # Extract the path coordinates from the data
        path = data['3D']['path']
        path_x = path[:int(self.current_measurement_id), 0] # Extract path up to the current measurement
        path_y = path[:int(self.current_measurement_id), 1]
        path_z = path[:int(self.current_measurement_id), 2]

        X_flat = data['3D']['X'].flatten()
        Y_flat = data['3D']['Y'].flatten()
        Z_flat = data['3D']['Z'].flatten()

        ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points', s = 5)
        ax.plot(path_x, path_y, path_z, color='red', label='Path')
        ax.legend()

        # Plot the seethrough plane
        if data["Slices"] != {}:

            # Extract Meshgrid from Data
            slice_index = str(tab.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("slice_slider").get())
            first_measurement_id = list(data["Slices"][slice_index].keys())[0]
            z = int(data["Slices"][slice_index][first_measurement_id]["Measurement_point"][2]) # Get the z value of the first measurement point in the slice
            
            X_plane = data["3D"]["X"][:,:,z]
            Y_plane = data["3D"]["Y"][:,:,z]

            Z_plane = np.full_like(X_plane, z)

            self.log_event(f"X Plane: {X_plane}")
            self.log_event(f"Y Plane: {Y_plane}")
            self.log_event(f"Z Plane: {Z_plane}")
            
            # Plot the plane
            ax.plot_surface(X_plane, Y_plane, Z_plane, color='blue', alpha=0.3, rstride=100, cstride=100)
        
        canvas.draw()

        #self.log_event(f"Updated measurement info for Tab {self.tab_count}")
    def update_progress_bar(self, progress_bar, measurements_done):
        
        progress_bar["value"] = measurements_done
        progress_bar.update_idletasks()
    def update_sensor_info_frame(self, tab, data):
            
        sensor_info_frame = tab.nametowidget("sensor_info_frame")
        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")

        current_measurement_data = data["Measurements"][self.current_measurement_id]

        # Update the sensor readings
        xpos_label = sensor_readings_frame.nametowidget("xpos_label")
        ypos_label = sensor_readings_frame.nametowidget("ypos_label")
        xdiff_label = sensor_readings_frame.nametowidget("xdiff_label")
        ydiff_label = sensor_readings_frame.nametowidget("ydiff_label")
        sum_label = sensor_readings_frame.nametowidget("sum_label")

        xpos_label.config(text=f"X Position: {current_measurement_data['Signal_xpos']}")
        ypos_label.config(text=f"Y Position: {current_measurement_data['Signal_ypos']}")
        xdiff_label.config(text=f"X Diff: {current_measurement_data['Signal_xdiff']}")
        ydiff_label.config(text=f"Y Diff: {current_measurement_data['Signal_ydiff']}")
        sum_label.config(text=f"Sum: {current_measurement_data['Signal_sum']}")

        """ # TODO might be redundant
        # Update the sensor position
        sensor_position_frame = sensor_info_frame.nametowidget("sensor_position_frame")
        sensor_position_x_label = sensor_position_frame.nametowidget("sensor_position_x_label")
        sensor_position_y_label = sensor_position_frame.nametowidget("sensor_position_y_label")
        sensor_position_z_label = sensor_position_frame.nametowidget("sensor_position_z_label")
        sensor_rotation_label = sensor_position_frame.nametowidget("sensor_rotation_label")
        sensor_distance_to_probe_label = sensor_position_frame.nametowidget("sensor_distance_to_probe_label")

        sensor_position_x_label.config(text=f"X Position: {current_measurement_data['Sensor_xpos']}")
        sensor_position_y_label.config(text=f"Y Position: {current_measurement_data['Sensor_ypos']}")
        sensor_position_z_label.config(text=f"Z Position: {current_measurement_data['Sensor_zpos']}")
        #sensor_rotation_label.config(text=f"Rotation: {current_measurement_data['Sensor_rotation']}")
        # TODO calculate distance to probe and show it here
        """

        # Plot the x pos and y pos in sensor_plot_frame
        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        canvas = sensor_plot_frame.canvas 
        ax = canvas.figure.axes[0]
        ax.clear() #TODO after all dots have been shown, dont clear any more

        # Plot all previous points in black
        for measurement_id in range(1, int(self.current_measurement_id)):
            previous_measurement_data = data["Measurements"][str(measurement_id)]
            ax.plot(previous_measurement_data['Signal_xpos'], previous_measurement_data['Signal_ypos'], 'o', color='black')

        # Plot the current point in red
        ax.plot(current_measurement_data['Signal_xpos'], current_measurement_data['Signal_ypos'], 'o', color='red')

        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_title('Sensor Output')
        ax.grid(True)
        ax.legend(['Signal Position'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        sensor_plot_frame.canvas.draw()

        #self.log_event(f"Updated sensor info for Tab {tab}")
    def update_slice_plot(self, event=None):
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        data = self.data # TODO implement multiple different data storages handling

        results_frame = tab.nametowidget("results_frame")
        slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
        plot_frame = slice_plot_frame.nametowidget("plot_frame")

        canvas = plot_frame.canvas
        ax = canvas.figure.axes[0]

        slice_slider = slice_plot_frame.nametowidget("slice_slider")
        interpolation_checkbox = slice_plot_frame.nametowidget("interpolation_checkbox")

        contour_levels_slider = slice_plot_frame.nametowidget("contour_levels_slider")
        contour_levels = contour_levels_slider.get()
        
        interpolation_var = interpolation_checkbox.value.get()
        interpolation = interpolation_var

        slice_index = str(slice_slider.get()) # fix slider bug
        self.log_event(f"Slice Index: {slice_index}")

        #only update if data is available
        if data["Slices"] != {}:
            # Get the slice from the data
            slice = data["Slices"][slice_index] # TODO implement multiple different data storages handling
            
            points = []
            sum_values = []

            for measurement_id in slice:
                point = slice[measurement_id]["Measurement_point"]
                sum = slice[measurement_id]["Signal_sum"]
                sum = int(sum*100) # scale the sum value
                points.append(point)
                sum_values.append(sum)
                #print(f"Point: {point}, Sum: {sum}")

        
            x_coords = [point[0] for point in points]
            y_coords = [point[1] for point in points]

            # Create grid data
            x = np.linspace(min(x_coords), max(x_coords), 100) # TODO maybe be related to len(sum_values)
            y = np.linspace(min(y_coords), max(y_coords), 100)
            X, Y = np.meshgrid(x, y)
            Z = np.zeros_like(X)

            # Interpolate sum values onto the grid
            interpolation_method = 'nearest' if interpolation_var == 0 else 'cubic'
            Z = griddata((x_coords, y_coords), sum_values, (X, Y), method=interpolation_method)
            

            # Update the slice plot
            ax.clear()
            contour = ax.contourf(X, Y, Z, levels=contour_levels, cmap='hot') # TODO 
            canvas.draw()


            self.update_measurement_info_frame(tab, data)
        

            self.log_event("Updated Slice Plot")
        else:
            self.log_event("No Slice Data available")

    # Button Functions
    def start_button_pushed(self):
        self.create_tab()
        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)
        self.log_event("Start button pushed")

        # Get the grid size and step size
        self.grid_size = self.new_measurement_panel.nametowidget("input_frame").nametowidget("measurement_space_entry").get()
        self.grid_size = tuple(map(int, self.grid_size.split(',')))
        self.step_size = float(self.new_measurement_panel.nametowidget("input_frame").nametowidget("step_size_entry").get())

        # Get the Measurment points and path points
        X, Y, Z = generate_grid(self.grid_size, self.step_size)
        self.grid = (X, Y, Z)
        self.path_points = generate_snake_path(X, Y, Z)
        self.add_3D_data(self.data, self.grid, self.grid_size, self.step_size, self.path_points)
         
        self.measurement_points = self.data["3D"]["measurement_points"]
        self.data["Measurements"] = {} # Create a dictionary to store the measurements
        self.data["Slices"] = {} # Create a dictionary to store the slices

        self.start_time = time.time()
        self.elapsed_time = 0

        self.add_meta_data(self.data)

        measurement_slider = tab.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
        measurement_slider.config(to=self.measurement_points)

        progress_bar = self.new_measurement_panel.nametowidget("progress_bar")
        progress_bar['maximum'] = self.measurement_points
        
        # Start the measurement
        for i in range(self.measurement_points):
            self.log_event(f"Measurement {i+1} of {self.measurement_points}")


            next_relative_position = (self.path_points[i][0], self.path_points[i][1], self.path_points[i][2], 0, 0, 0) # account for rotation
            #self.hexapod.move(next_relative_position, flag = "relative") # TODO move Hexapod to next position
            #wait for hexapod to move

            self.doMeasurement(self.data, self.sensor, i)
            
            # update 
            measurement_slider.set(str(i+1))
            self.update_progress_bar(progress_bar, i+1) # TODO add this to new_measurement_panel
            self.update_tab()

            self.elapsed_time = time.time() - self.start_time
            self.data["info"]["elapsed_time"] = self.elapsed_time

        self.create_slices(self.data)

        #pprint.pprint(self.data)   # Show Data structure in Console

        self.update_tab()

        measurement_slider.config(state = "normal")
        self.new_measurement_panel.nametowidget("save_button").config(state="normal")
        self.log_event("Done with measurements")       
    def save_button_pushed(self):
        folder_path = 'C:/Users/Valen/OneDrive/Dokumente/uni_Dokumente/Classes/WiSe2025/Thesis/Actual Work/data'
        file_name = filedialog.asksaveasfilename(initialdir=folder_path, filetypes=[("h5 files", "*.h5")])
        self.save_data(file_name, self.data)
        #messagebox.showinfo("Save Data", f"Data saved to {file_name}")
        self.log_event(f"Data saved to {file_name}")
    def load_button_pushed(self):
        file_path = filedialog.askopenfilename(filetypes=[("htm5 files", "*.h5")])
        if file_path:
            self.data = self.load_data(file_path)
            print(self.data)
            self.create_tab()
            self.update_tab()
            self.log_event(f"Data loaded from {file_path}")
   
    # Data Handling
    def save_data(self, data_folder, data):
        """
        Save the data to an HDF5 file.

        Parameters:
        data_folder (str): The folder to store the data.
        data (dict): The data to store, with keys for each measurement.
        """
        # Ensure the folder exists
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        # Define the HDF5 file path
        hdf5_file_path = os.path.join(data_folder, 'experiment_data.h5')

        # Write data to HDF5
        with h5py.File(hdf5_file_path, 'w') as hdf5_file:
            for key, value in data.items():
                key_str = str(key)  # Convert key to string
                if isinstance(value, (list, tuple)):
                    value = np.array(value)  # Convert lists or tuples to numpy arrays
                if isinstance(value, dict):
                    group = hdf5_file.create_group(key_str)
                    for sub_key, sub_value in value.items():
                        sub_key_str = str(sub_key)
                        if isinstance(sub_value, (list, tuple)):
                            sub_value = np.array(sub_value)
                        if sub_value is not None:
                            group.create_dataset(sub_key_str, data=sub_value)
                        else:
                            print(f"Skipping None value for {sub_key_str}")
                else:
                    if value is not None:
                        hdf5_file.create_dataset(key_str, data=value)
                    else:
                        print(f"Skipping None value for {key_str}")

        print(f"Data saved to {hdf5_file_path}") 
    def load_data(self, hdf5_file_path):

        with h5py.File(hdf5_file_path, 'r') as hdf5_file:
            data = {}
            for key in hdf5_file.keys():
                group = hdf5_file[key]
                if isinstance(group, h5py.Group):
                    data[key] = {sub_key: group[sub_key][()] for sub_key in group.keys()}
                else:
                    data[key] = group[()]
        return data
    def add_meta_data(self, data):
        data["camera"] = {
         
            "ret": self.ret,
            "mtx": self.mtx,
            "dist": self.dist,
            "rvecs": self.rvecs,
            "tvecs": self.tvecs
        }

        data["info"] = {

            "time_estimated": self.time_estimated,
            "elapsed_time": self.elapsed_time,
            "start_time": self.start_time
        }

        data["beam_visualization"] = {

            #TODO add beam visualization data here

        }
    def add_3D_data(self, data, grid, grid_size, step_size, path):
        data["3D"] = {
            "grid": grid, # (X, Y, Z)
            "X": grid[0],
            "Y": grid[1],
            "Z": grid[2],
            "grid_size": grid_size,
            "step_size": step_size,
            "path": path, 
            "measurement_points": len(path)
        } 
    
    # Measurement Handling
    def estimate_time(self):
        # TODO implement time estimation
        self.time_estimated = self.measurement_points * self.step_size # TODO replace with actual time estimation
        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("time_estimated_label").config(text="Time Estimated: " + str(self.time_estimated) + " [min]")

        self.log_event(f"Estimated time: " + str(self.time_estimated) + " [min]")

    def connect_hexapod(self):
        #TODO implement hexapod connection

        checkbox_panel = self.new_measurement_panel.nametowidget("checkbox_panel")
        connection_frame = checkbox_panel.nametowidget("connection_frame")

        server_ip = connection_frame.nametowidget("ip_entry").get()
        port_1 = int(connection_frame.nametowidget("port_1_entry").get())
        port_2 = int(connection_frame.nametowidget("port_2_entry").get())

        hexapod_connection_status = self.hexapod.connect_sockets(server_ip, port_1, port_2) # TODO change to true default ports
        if hexapod_connection_status == True:
            self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("hexapod_connected").select()
            self.log_event("Hexapod connected to Server")
        else:
            self.log_event("Connection to Server failed")

    def rough_alignment(self):
        #TODO implement rough alignment
        #self.hexapod.move_to_default_position()
        
        # Determine the rough alignment
        # Get Sensor Postion

        
        #relative_movement = self.sensor.position - self.probe.position # TODO implement sensor position
        # TODO implement some leeway for the rough alignment to avoid overshooting/collisions
        #server_response = self.hexapod.move(relative_movement, flag = "relative") # Move the Hexapod to the rough alignment position
        

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("rough_alignment").select()
        self.log_event("Rough Alignment done")
    
    def fine_alignment(self):
        fine_alignment(self.sensor, self.hexapod) # imported from another file

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("fine_alignment").select()
        self.log_event("Fine Alignment done")


    def create_slices(self, data): # TODO test this function
        last_z = None
        last_measurement_id = 0
        slice_index = 1 # Start with slice 1
        

        current_slice = {}

        for measurement_id in data["Measurements"]:
            measurement = data["Measurements"][str(measurement_id)]
            point = measurement["Measurement_point"]
            current_z = point[2] # TODO check if this is the correct axis

            if last_z is None:
                last_z = current_z # for first iteration

            if current_z != last_z:
                # Store the current slice
                data["Slices"][str(slice_index)] = current_slice
                slice_index += 1
                current_slice = {}

            current_slice[measurement_id] = measurement
            last_z = current_z
            last_measurement_id = measurement_id

        # Store the last slice
        if current_slice:
            data["Slices"][str(slice_index)] = current_slice


        # Set Slider limits
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        slice_slider = tab.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("slice_slider")
        slice_slider.config(from_=1, to=len(data["Slices"]))

        self.log_event("Created Slices")
    def doMeasurement(self, data, sensor, i):

        # Simulate a measurement TODO delete or comment this
        signal = sensor.get_test_signal() # TODO replace with sensor.get_readings()

        measurement_id_str = str(i+1)  # Convert measurement_id to string
        data["Measurements"][measurement_id_str] = {
            
            'Signal_xpos': signal.xpos,
            'Signal_ypos': signal.ypos,
            'Signal_xdiff': signal.xdiff,
            'Signal_ydiff': signal.ydiff,
            'Signal_sum': signal.sum,

            'Measurement_point': self.path_points[i],
        }
        self.log_event(f"Performed measurement {measurement_id_str}")
    def process_data(self, data):
        # Process the data
        self.log_event("Processing data")


if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()