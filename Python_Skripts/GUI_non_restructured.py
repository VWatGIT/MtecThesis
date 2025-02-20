import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import pprint
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pypylon.pylon as pylon
from scipy.interpolate import griddata
import os
import time
from datetime import datetime



from Function_Groups.camera import calibrate_camera, capture_image
from Function_Groups.object3D import Sensor, Probe, Hexapod
from Function_Groups.path_creation import generate_grid, generate_snake_path
from Function_Groups.probe_tip_detection import detect_needle_tip
from Function_Groups.probe_tip_detection import crop_image
from Function_Groups.probe_tip_detection import crop_coordinate_transform
from Function_Groups.marker_detection import detect_markers
from Function_Groups.data_handling import save_data, load_data
from Function_Groups.beam_visualization import create_heatmap
from Function_Groups.beam_visualization import process_slices
from Function_Groups.beam_visualization import create_slices
from Function_Groups.Simulation_of_Gauss_Beam import Gauss_Beam # Used for testing
from Function_Groups.Simulation_of_Gauss_Beam import create_Test_Beam # Used for testing
from GUI_Panels import ManualAdjustPanel

from Testing_Scripts.Beam_Trajectory import calculate_alpha_beta
from Testing_Scripts.Beam_Trajectory import plot_alpha_beta




#from GUI_Panels import *
#from Function_Groups import *
class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Probe Beam Measurement")
        self.root.geometry("1920x1080")
        self.root.wm_state("zoomed")

        self.tab_count = -1
        
        # Create the objects
        self.sensor = Sensor()
        self.probe = Probe()
        self.hexapod = Hexapod()
        self.gauss_beam = create_Test_Beam() 

        # Default values
        self.grid_size = (1, 6, 6) #mm

        self.step_size = (1,1,1) #mm
        
        # TODO attach these values to tab
        self.measurement_points = 1
        self.time_estimated = 0
        self.elapsed_time = 0 
        self.current_measurement_id = 0

        self.measurement_running = False


        os.environ["PYLON_CAMEMU"] = "1" # Enable the pylon camera emulator for testing at home
        self.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = None , None, None, None , None # Camera Calibration Values
        self.camera_calibrated = False # TODO replace with variable from GUI?

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

        # Setup
        #root.after(100, self.setup) # after to give the event log time to be created
   
    def setup(self):
        self.connect_stage() # TODO decide if necessary
        self.connect_hexapod()
    def new_data(self): # attach this to the new tab
        data = {}
        data["3D"] = {}
        data["Measurements"] = {}
        data['Info'] = {}
        data['Visualization'] = {}
        data['Visualization']['Slices'] = {}
        data['Beam_Parameters'] = {}
        
        return data

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

        for i in range(9):
            input_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            input_frame.grid_columnconfigure(i, weight=1)

        probe_name_label = tk.Label(input_frame, text="Probe Name:")
        probe_name_label.grid(row=0, column=0, pady=5, sticky="e")
        self.probe_name_entry = tk.Entry(input_frame, name="probe_name_entry")
        self.probe_name_entry.grid(row=0, column=1, pady=5, sticky = "w")
        self.probe_name_entry.insert(0, "Default")

        # TODO maybe add aditional input fields for new measurement

        measurement_space_label = tk.Label(input_frame, text="3D Size: [mm]")
        measurement_space_label.grid(row=1, column=0, pady=5, sticky="e")
        self.measurement_space_entry = tk.Entry(input_frame, name = "measurement_space_entry")
        self.measurement_space_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.measurement_space_entry.insert(0, f"{self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]}")

        #Set up inputs for Step Size
        step_size_label = tk.Label(input_frame, text="Step Size: [mm]")
        step_size_label.grid(row=2, column=0, pady=5, sticky="e")
        self.step_size_entry = tk.Entry(input_frame, name = "step_size_entry")
        self.step_size_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.step_size_entry.insert(0, f"{self.step_size[0]}, {self.step_size[1]}, {self.step_size[2]}") 

        # Time estimation
        time_estimated_label = tk.Label(input_frame, text="Estimated Time: N/A ", name="time_estimated_label") 
        time_estimated_label.grid(row=3, column=0, pady=5, sticky="w")

        time_estimation_button = tk.Button(input_frame, text="Estimate Time", command=self.estimate_time)
        time_estimation_button.grid(row=3, column=1, pady=5, sticky="w")

        wavelength_label = tk.Label(input_frame, text="Wavelength [nm]:")
        wavelength_label.grid(row=4, column=0, pady=5, sticky="e")
        self.wavelength_entry = tk.Entry(input_frame, name="wavelength_entry")
        self.wavelength_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.wavelength_entry.insert(0, "1300")

        w_0_label = tk.Label(input_frame, text="Beam Waist [mm]:")
        w_0_label.grid(row=5, column=0, pady=5, sticky="e")
        self.w_0_entry = tk.Entry(input_frame, name="w_0_entry")
        self.w_0_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.w_0_entry.insert(0, "1")

        i_0_label = tk.Label(input_frame, text="I_0 [W/m^2]:")
        i_0_label.grid(row=6, column=0, pady=5, sticky="e")
        self.i_0_entry = tk.Entry(input_frame, name="i_0_entry")
        self.i_0_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.i_0_entry.insert(0, "60000")

        alpha_label = tk.Label(input_frame, text="Simulate Pitch [deg]:")
        alpha_label.grid(row=7, column=0, pady=5, sticky="e")
        self.alpha_entry = tk.Entry(input_frame, name="alpha_entry")
        self.alpha_entry.grid(row=7, column=1, pady=5, sticky="w")
        self.alpha_entry.insert(0, "0")

        beta_label = tk.Label(input_frame, text="Simulate Yaw [deg]:")
        beta_label.grid(row=8, column=0, pady=5, sticky="e")
        self.beta_entry = tk.Entry(input_frame, name="beta_entry")
        self.beta_entry.grid(row=8, column=1, pady=5, sticky="w")
        self.beta_entry.insert(0, "0")

        #Set up checkboxes
        checkbox_panel = tk.Frame(self.new_measurement_panel, name="checkbox_panel")
        checkbox_panel.grid(row=2, column=0, columnspan=2, padx= 10, pady=5, sticky="nsew")

        for i in range(9):
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
        self.ip_entry.insert(0, '134.28.45.17') # TODO change to default value

        connect_hexapod_button = tk.Button(connection_frame, text="Connect Hexapod", command=self.connect_hexapod)
        connect_hexapod_button.grid(row=3, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")

        stage_connected = tk.Checkbutton(checkbox_panel, text="Stage connected", name="stage_connected", state="disabled")
        stage_connected.grid(row=5, column=0, pady=5, sticky="w")

        connect_stage_button = tk.Button(checkbox_panel, text="Connect Stage", command=self.connect_stage)
        connect_stage_button.grid(row=5, column=1, pady=5, sticky="w")

        rough_alignment = tk.Checkbutton(checkbox_panel, text="Rough Alignment", name="rough_alignment", state="disabled")
        rough_alignment.grid(row=6, column=0, pady=5, sticky="w")

        rough_alignment_button = tk.Button(checkbox_panel, text="Rough Align", command=self.rough_alignment)
        rough_alignment_button.grid(row=6, column=1, pady=5, sticky="w")

        fine_alignment = tk.Checkbutton(checkbox_panel, text="Fine Alignment", name="fine_alignment", state="disabled") # gets enabled after rough alignment
        fine_alignment.grid(row=7, column=0, pady=5, sticky="w") 

        fine_alignment_button = tk.Button(checkbox_panel, text="Fine Align", command=self.fine_alignment)
        fine_alignment_button.grid(row=7, column=1, pady=5, sticky="w")


        progress_bar = ttk.Progressbar(self.new_measurement_panel, orient="horizontal", length=320, mode="determinate", name="progress_bar")
        progress_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        self.simulate_var = tk.IntVar()
        simulate_checkbox = tk.Checkbutton(self.new_measurement_panel, text="Simulate", name="simulate_checkbox", variable=self.simulate_var)
        simulate_checkbox.grid(row=3, column=0, pady=5, sticky="nsew")

        self.autosave_var = tk.IntVar()
        autosave_checkbox = tk.Checkbutton(self.new_measurement_panel, text="Autosave", name="autosave_checkbox", variable=self.autosave_var)
        autosave_checkbox.grid(row=3, column=1, pady=5, sticky="nsew")
        #autosave_checkbox.select()

        #Set up Big Buttons
        #self.new_measurement_panel.grid_rowconfigure(3, weight=10)

        start_button = tk.Button(self.new_measurement_panel, text="START", name="start_button", command=self.start_button_pushed, width = 20, height = 3)
        start_button.grid(row=4, column=0, padx=10, pady=5, sticky = "w")

        save_button = tk.Button(self.new_measurement_panel, text="SAVE",name="save_button", command=self.save_button_pushed, width = 20, height =3, state="disabled")
        save_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")

        stop_button = tk.Button(self.new_measurement_panel, text="STOP", name="stop_button", command=self.stop_button_pushed, width = 30, height = 5)
        stop_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

    def create_load_measurement_panel(self, parent):
        self.load_measurement_panel = tk.Frame(parent)

        load_button = tk.Button(self.load_measurement_panel, text="LOAD", command=self.load_button_pushed, width=20, height=3)
        load_button.pack(pady=30)

        return_button = tk.Button(self.load_measurement_panel, text="Return", command=self.show_home_panel, width=20, height=3)
        return_button.pack(pady=30)
    def create_camera_panel(self, parent):
        self.camera_panel = ttk.Notebook(parent, name="camera_panel") # notebook to save time TODO rename
        self.camera_panel.place(relx=1, rely=1, anchor="center", relheight=1, relwidth=1)

        for i in range(2):
            self.camera_panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.camera_panel.grid_columnconfigure(i, weight=1)
 
        self.create_camera_settings_frame(self.camera_panel)
        self.create_camera_calibration_frame(self.camera_panel)
        self.create_probe_detection_frame(self.camera_panel)
        self.create_marker_detection_frame(self.camera_panel)
        
        
        self.probe_detection_frame = self.camera_panel.nametowidget("probe_detection_frame")
        self.marker_detection_frame = self.camera_panel.nametowidget("marker_detection_frame")
        self.camera_settings_frame = self.camera_panel.nametowidget("camera_settings_frame")
        self.camera_calibration_frame = self.camera_panel.nametowidget("camera_calibration_frame")
        
        
        #self.marker_detection_frame.pack(side = "right", fill="both", expand=True)
        #self.probe_detection_frame.pack(side = "left", fill="both", expand=True)

        self.camera_panel.add(self.camera_calibration_frame, text="Calibration")
        self.camera_panel.add(self.probe_detection_frame, text="Probe-Tip")
        self.camera_panel.add(self.marker_detection_frame, text="Markers")
        self.camera_panel.add(self.camera_settings_frame, text="Info")
        

        return_button = tk.Button(self.camera_panel, text="Return", command= lambda: self.camera_panel.place_forget())
        return_button.place(relx=1, rely= 0, anchor="ne")
    def create_help_panel(self, parent):
        self.help_panel = tk.Frame(parent, name="help_panel")
        
        manual_adjust_panel = ManualAdjustPanel(self.help_panel, self.manual_alignment).panel
        manual_adjust_panel.pack(side="left", expand=True)

        """
        self.manual_adjust_panel = tk.LabelFrame(self.help_panel,text="Adjust Hexapod Positon",name="manual_adjust_panel")
        self.manual_adjust_panel.pack(side="left", expand=True)

        for i in range(10):
            self.manual_adjust_panel.grid_rowconfigure(i, weight=1)
        for i in range(4):
            self.manual_adjust_panel.grid_columnconfigure(i, weight=1)

        e_width = 10

        hexapod_x_label = tk.Label(self.manual_adjust_panel, text="X: ")
        hexapod_x_label.grid(row=0, column=0, pady=5, sticky="e")
        self.hexapod_x_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_x_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.hexapod_x_entry.insert(0, "0")

        hexapod_y_label = tk.Label(self.manual_adjust_panel, text="Y: ")
        hexapod_y_label.grid(row=1, column=0, pady=5, sticky="e")
        self.hexapod_y_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_y_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.hexapod_y_entry.insert(0, "0")

        hexapod_z_label = tk.Label(self.manual_adjust_panel, text="Z: ")
        hexapod_z_label.grid(row=2, column=0, pady=5, sticky="e")
        self.hexapod_z_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_z_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.hexapod_z_entry.insert(0, "0")

        seperator = ttk.Separator(self.manual_adjust_panel, orient="horizontal")
        seperator.grid(row=3, column=0, columnspan=4, sticky="ew", pady=5)

        hexapod_U_label = tk.Label(self.manual_adjust_panel, text="U: ")
        hexapod_U_label.grid(row=4, column=0, pady=5, sticky="e")
        self.hexapod_U_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_U_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.hexapod_U_entry.insert(0, "0")

        hexapod_V_label = tk.Label(self.manual_adjust_panel, text="V: ")
        hexapod_V_label.grid(row=5, column=0, pady=5, sticky="e")
        self.hexapod_V_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_V_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.hexapod_V_entry.insert(0, "0")

        hexapod_W_label = tk.Label(self.manual_adjust_panel, text="W: ")
        hexapod_W_label.grid(row=6, column=0, pady=5, sticky="e")
        self.hexapod_W_entry = tk.Entry(self.manual_adjust_panel, width=e_width)
        self.hexapod_W_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.hexapod_W_entry.insert(0, "0")

        # Increment Buttons
        hexapod_x_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_x_entry, 0.1)
        hexapod_x_increment_button.grid(row=0, column=2, pady=5, sticky="w")
        hexapod_x_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_x_entry, -0.1)
        hexapod_x_decrement_button.grid(row=0, column=3, pady=5, sticky="w")

        hexapod_y_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_y_entry, 0.1)
        hexapod_y_increment_button.grid(row=1, column=2, pady=5, sticky="w")
        hexapod_y_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_y_entry, -0.1)
        hexapod_y_decrement_button.grid(row=1, column=3, pady=5, sticky="w")

        hexapod_z_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_z_entry, 0.1)
        hexapod_z_increment_button.grid(row=2, column=2, pady=5, sticky="w")
        hexapod_z_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_z_entry, -0.1)
        hexapod_z_decrement_button.grid(row=2, column=3, pady=5, sticky="w")

        hexapod_U_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_U_entry, 0.1)
        hexapod_U_increment_button.grid(row=4, column=2, pady=5, sticky="w")
        hexapod_U_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_U_entry, -0.1)
        hexapod_U_decrement_button.grid(row=4, column=3, pady=5, sticky="w")

        hexapod_V_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_V_entry, 0.1)
        hexapod_V_increment_button.grid(row=5, column=2, pady=5, sticky="w")
        hexapod_V_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_V_entry, -0.1)
        hexapod_V_decrement_button.grid(row=5, column=3, pady=5, sticky="w")

        hexapod_W_increment_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_W_entry, 0.1)
        hexapod_W_increment_button.grid(row=6, column=2, pady=5, sticky="w")
        hexapod_W_decrement_button = self.create_increment_button(self.manual_adjust_panel, self.hexapod_W_entry, -0.1)
        hexapod_W_decrement_button.grid(row=6, column=3, pady=5, sticky="w")

        seperator2 = ttk.Separator(self.manual_adjust_panel, orient="horizontal")
        seperator2.grid(row=7, column=0, columnspan=4, sticky="ew", pady=5)

        def set_to_0():
            self.hexapod_x_entry.delete(0, "end")
            self.hexapod_x_entry.insert(0, "0")
            self.hexapod_y_entry.delete(0, "end")
            self.hexapod_y_entry.insert(0, "0")
            self.hexapod_z_entry.delete(0, "end")
            self.hexapod_z_entry.insert(0, "0")
            self.hexapod_U_entry.delete(0, "end")
            self.hexapod_U_entry.insert(0, "0")
            self.hexapod_V_entry.delete(0, "end")
            self.hexapod_V_entry.insert(0, "0")
            self.hexapod_W_entry.delete(0, "end")
            self.hexapod_W_entry.insert(0, "0")
        set_to_0_button = tk.Button(self.manual_adjust_panel, text="Set 0", command=set_to_0)
        set_to_0_button.grid(row=8, column=3,columnspan=2,rowspan=2, pady=5, sticky="w")

        self.relative_checkbutton_var = tk.IntVar()

        self.relative_checkbutton = tk.Checkbutton(self.manual_adjust_panel, text="Relative", name="relative_checkbutton", variable=self.relative_checkbutton_var)
        self.relative_checkbutton.grid(row=8, column=0,columnspan=2,pady=5, sticky="ns")
        #self.relative_checkbutton.rowconfigure(8, weight=100)

        manual_align_button = tk.Button(self.manual_adjust_panel, text="Confirm", command=self.manual_alignment)
        manual_align_button.grid(row=9, column=0, columnspan= 2, pady=5, sticky="ns")
        #self.manual_adjust_panel.rowconfigure(8, weight=100)
        """
    def create_increment_button(self, parent, entry_field, increment):
        def increment_entry(entry_field, increment):
            current_value = entry_field.get()
            new_value = round(float(current_value) + increment, 4)

            entry_field.delete(0, "end")
            entry_field.insert(0, str(new_value))
        
        if np.sign(increment) > 0:
            increment_button = tk.Button(parent, text=f"+{increment}", command=lambda: increment_entry(entry_field, increment))
        else:
            increment_button = tk.Button(parent, text=f"{increment}", command=lambda: increment_entry(entry_field, increment))
        
        return increment_button


    def show_home_panel(self):
        self.hide_all_panels()
        self.home_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_new_measurement_panel(self):
        self.hide_all_panels()
        self.show_tabgroup()
        self.new_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_load_measurement_panel(self):
        self.hide_all_panels()
        self.show_tabgroup()
        self.load_measurement_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_camera_panel(self):
        self.help_panel.place_forget()
        self.camera_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_help_panel(self):
            self.camera_panel.place_forget()
            self.help_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def show_tabgroup(self):
        self.help_panel.place_forget()
        self.camera_panel.place_forget()
        self.tab_group.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    def hide_all_panels(self):
        self.home_panel.place_forget()
        self.new_measurement_panel.place_forget()
        self.load_measurement_panel.place_forget()
        self.camera_panel.place_forget()
        self.help_panel.place_forget()

    def create_camera_plot_frame(self, parent):
        camera_plot_frame = tk.LabelFrame(parent, text="Camera Image", name="camera_plot_frame")
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=camera_plot_frame)
        canvas.get_tk_widget().place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
        camera_plot_frame.canvas = canvas
        ax.axis('off')
        return camera_plot_frame
    def create_camera_settings_frame(self, parent):
        self.camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        toggle_camera_button = tk.Checkbutton(self.camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera)
        toggle_camera_button.pack(side = "top", pady=5)
    def create_probe_detection_frame(self, parent):
        probe_detection_frame = tk.LabelFrame(parent, text="Probe Tip", name="probe_detection_frame")
        
        for i in range(2):
            probe_detection_frame.grid_rowconfigure(i, weight=1)
        for i in range(1):
            probe_detection_frame.grid_columnconfigure(i, weight=1)

        self.create_probe_detection_input_frame(probe_detection_frame)
        
        self.probe_detection_input_frame = probe_detection_frame.nametowidget("probe_detection_input_frame")
        self.probe_detection_input_frame.grid(row=0, column=0, pady=5, sticky = "n")

        # Create a frame for the probe plot
        self.probe_plot_frame = tk.Frame(probe_detection_frame, name="probe_plot_frame")
        self.probe_plot_frame.grid(row=1, column=0, pady=5, sticky = "nsew")

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
        self.threshold_slider.config(command=self.take_probe_image)


        self.take_probe_image_button = tk.Button(probe_detection_input_frame, text="Take Image", command=self.take_probe_image) 
        self.take_probe_image_button.grid(row=4, column=0, columnspan=2,rowspan = 2,pady=5)

        probe_detection_input_frame.grid_rowconfigure(3, weight=3) #weight row for gap
        
        self.save_probe_position_button = tk.Button(probe_detection_input_frame, text="Save Position", command=self.save_probe_position, state="disabled") # TODO implement detect_probe
        self.save_probe_position_button.grid(row=6, column=1, pady=5)

        self.probe_detetection_checkbox = tk.Checkbutton(probe_detection_input_frame, text="Probe Detected", name="probe_detected", state="disabled")
        self.probe_detetection_checkbox.grid(row=6, column=0, pady=5)
    def create_marker_detection_frame(self, parent):
        marker_detection_frame = tk.LabelFrame(parent, text="Marker Detection", name="marker_detection_frame")
        self.camera_plot_frame = self.create_camera_plot_frame(marker_detection_frame)
        marker_stats_frame = self.create_marker_stats_frame(marker_detection_frame)

        for i in range(2):
            marker_detection_frame.grid_rowconfigure(i, weight=1)
        for i in range(1):
            marker_detection_frame.grid_columnconfigure(i, weight=1)

        self.camera_plot_frame.grid(row=0, column=0, pady=5, sticky="nsew")
        marker_stats_frame.grid(row=1, column=0, pady=5, sticky="nsew")
    def create_marker_stats_frame(self, parent):
        marker_stats_frame = tk.Frame(parent, name="marker_stats_frame")

        return marker_stats_frame
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
            self.camera_calibrated = True
            self.log_event("Calibrated Camera")
        else:
            self.log_event("Calibration failed: No valid checkerboard corners found in any image")
    def update_camera(self):    
        if self.camera.IsOpen():
            image = capture_image(self.camera)


            if self.camera_calibrated:
                image, marker_rvecs, marker_tvecs = detect_markers(image, self.mtx, self.dist)

                self.sensor.marker_rvecs = marker_rvecs[self.sensor.marker_id]
                self.sensor.marker_tvecs = marker_tvecs[self.sensor.marker_id]
                self.probe.marker_rvecs = marker_rvecs[self.probe.marker_id]
                self.probe.marker_tvecs = marker_tvecs[self.probe.marker_id]

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
        self.paned_window.add(self.helper_frame)

        self.create_event_log_panel(self.paned_window)
        self.paned_window.add(self.event_log_panel)

        self.create_tab_group(self.helper_frame)
        self.create_help_panel(self.helper_frame)
        self.create_camera_panel(self.helper_frame)
        
        
        

        #self.paned_window.config(sashrelief="raised")
        self.root.after(200, lambda: self.paned_window.sashpos(0, 840)) # set initial position of sash, after for short delay (bugfix)
        
        self.update_log()
    def create_tab_group(self, parent):
        self.tab_group = ttk.Notebook(parent, name="tab_group")
        self.tab_group.pack(side="right", fill="both", expand=True)

        self.create_tab() # Create the Default Tab
    def create_tab(self, data = None):
        self.tab_count += 1
        name = str(self.probe_name_entry.get()).lower() 

        new_tab = ttk.Frame(self.tab_group, name=f"{name}_{self.tab_count}")
        self.tab_group.add(new_tab, text=name)
        #self.tabs[self.tab_count] = new_tab
        if data == None:
            new_tab.data = self.new_data()
        else:
            new_tab.data = data 

        self.create_subtabs(new_tab)

        close_button = tk.Button(new_tab, text="Close Tab", command=lambda: self.close_tab(new_tab), name="close_button") # create this last in create_tab
        close_button.place(relx=1, rely=0, anchor="ne")  # Place the close button in the top-right corner

        self.tab_group.select(new_tab)

        # Log the creation of a new tab
        self.log_event(f"Created Tab {self.tab_count}") 
    def close_tab(self, tab):
        self.tab_group.forget(tab)
        self.log_event("Closed Tab") 
    def create_subtabs(self, parent):
        subtab_group = ttk.Notebook(parent, name="subtab_group")
        subtab_group.pack(side="right", fill="both", expand=True)

        self.create_results_frame(subtab_group)
        results_frame = subtab_group.nametowidget("results_frame")
        results_frame.pack(side="right", fill="both", expand=True)
        
        sensor_path_frame = tk.Frame(subtab_group, name="sensor_path_frame")
        
        self.create_sensor_info_frame(sensor_path_frame)
        sensor_info_frame = sensor_path_frame.nametowidget("sensor_info_frame")
        sensor_info_frame.pack(side="left", fill="both", expand=True)

        self.create_path_plot_frame(sensor_path_frame)
        path_plot_frame = sensor_path_frame.nametowidget("path_plot_frame")
        path_plot_frame.pack(side="right", fill="both", expand=True)


        self.create_measurement_info_frame(subtab_group)
        measurement_info_frame = subtab_group.nametowidget("measurement_info_frame")
        measurement_info_frame.pack(side="right", fill="both", expand=True)

        subtab_group.add(sensor_path_frame, text="Measurement")
        subtab_group.add(results_frame, text="Results")
        subtab_group.add(measurement_info_frame, text="Info")
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
    
        self.root.after(3000, self.update_log)  # Schedule the update function to run every 5 seconds

    def create_sensor_info_frame(self, parent):
        # Create the main sensor_info_frame LabelFrame
        sensor_info_frame = tk.LabelFrame(parent, text="Measurement N/A" , name="sensor_info_frame")#, width=500, height=500)
    
        # Configure the grid layout within the sensor_info_frame LabelFrame
        for i in range(2):
            sensor_info_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            sensor_info_frame.grid_rowconfigure(i, weight=1)

        self.create_sensor_readings_frame(sensor_info_frame)
        self.create_sensor_plot_frame(sensor_info_frame)

        measurment_slider = tk.Scale(sensor_info_frame, from_=1, to=100, orient="horizontal", name="measurement_slider")
        measurment_slider.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        sensor_info_frame.grid_rowconfigure(1, weight=100)
        sensor_info_frame.grid_columnconfigure(1, weight=100)

        measurment_slider.set(1)
        measurment_slider.config(resolution=1, state="normal", command=self.update_tab)
    
        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")
        sensor_readings_frame.grid(row=1, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)

        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        sensor_plot_frame.grid(row=1, column=0, columnspan=1, sticky="ns", padx=10, pady=10)      
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
        # Sensor Position Panel TODO delete or implement
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

        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_title('Sensor Output')
        ax.grid(True)
        ax.legend(['Signal Position'])

        ax.set_aspect('equal')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

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
        self.create_beam_plot_frame(results_frame)
        self.create_trajectory_plot_frame(results_frame)

        beam_plot_frame = results_frame.nametowidget("beam_plot_frame")
        beam_plot_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        trajectory_plot_frame = results_frame.nametowidget("trajectory_plot_frame")
        trajectory_plot_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
        slice_plot_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
    def create_slice_plot_frame(self, parent):
        slice_plot_frame = tk.LabelFrame(parent, text="Slice", name="slice_plot_frame")
        for i in range(7):
            slice_plot_frame.grid_rowconfigure(i, weight=1)
        for i in range(1): 
            slice_plot_frame.grid_columnconfigure(i, weight=1)
        
        vertical_plot_frame = tk.LabelFrame(slice_plot_frame, name="vertical_plot_frame")
        vertical_plot_frame.grid(row=2, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=5)
        slice_plot_frame.grid_rowconfigure(2, weight=100) #weight for correct sizing of the slider
      
        # Create a canvas for the slice plot
        fig, ax = plt.subplots()
        ax.set_xlabel('Y')
        ax.set_ylabel('Z')
        ax.set_title('Heatmap of Laser Beam')
        ax.invert_yaxis()  # invert y axis

        canvas = FigureCanvasTkAgg(fig, master=vertical_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both")
        vertical_plot_frame.canvas = canvas
        
        # Create Labels for the Sliders
        slice_slider_label = ttk.Label(slice_plot_frame, text=" Vertical Slice Index:", name="slice_slider_label")
        slice_slider_label.grid(row=0, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)

        # Create a slider for the slice plot
        vertical_slice_slider = tk.Scale(slice_plot_frame, from_=1, to=2, orient="horizontal", name="vertical_slice_slider")
        vertical_slice_slider.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        vertical_slice_slider.set(1) # set default value
        vertical_slice_slider.config(resolution=1) # set slider resolution

        # Create the horizontal plot frame
        horizontal_plot_frame = tk.LabelFrame(slice_plot_frame, name="horizontal_plot_frame")
        horizontal_plot_frame.grid(row=4, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=5)

        # Create a canvas for the horizonatl slice plot
        fig, ax = plt.subplots()
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_title('Horizontal Slice')
        
        canvas = FigureCanvasTkAgg(fig, master=horizontal_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both")  
        horizontal_plot_frame.canvas = canvas



        # Create a Slider for horizontal slice plot
        horizontal_slice_slider_label = ttk.Label(slice_plot_frame, text="Horizontal Slice Index:", name="horizontal_slice_slider_label")
        horizontal_slice_slider_label.grid(row=5, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)

        horizontal_slice_slider = tk.Scale(slice_plot_frame, from_=1, to=2, orient="horizontal", name="horizontal_slice_slider")
        horizontal_slice_slider.grid(row=6, column=0, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        horizontal_slice_slider.set(1) # set default value
        horizontal_slice_slider.config(resolution=1) # set slider resolution

        slice_plot_frame.grid_rowconfigure(4, weight=100) #weight for correct sizing of the slider

        # Create a checkbox for the slice plot
        interpolation_var = tk.IntVar()
        interpolation_checkbox = tk.Checkbutton(slice_plot_frame, text="Interpolation", name="interpolation_checkbox", variable=interpolation_var)
        interpolation_checkbox.grid(row=3, column=0, columnspan=1, sticky="w", padx=5, pady=5)
        interpolation_checkbox.value = interpolation_var

        vertical_slice_slider.config(command=self.update_slice_plot)
        horizontal_slice_slider.config(command=self.update_slice_plot)
        interpolation_checkbox.config(command=self.update_slice_plot) 
    def create_beam_plot_frame(self, parent):
        
        beam_plot_frame = tk.LabelFrame(parent, text="Beam Plot", name="beam_plot_frame")

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.set_title('Beam Plot')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        canvas = FigureCanvasTkAgg(fig, master=beam_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        beam_plot_frame.canvas = canvas

        pass
    def create_measurement_info_frame(self, parent):
        measurement_info_frame = tk.LabelFrame(parent, name="measurement_info_frame") 

        for i in range(2):
            measurement_info_frame.rowconfigure(i, weight = 1)
        for i in range(2):
            measurement_info_frame.columnconfigure(i, weight = 1)

        # General info 
        general_info_frame = tk.LabelFrame(measurement_info_frame, text = 'Info', name='general_info_frame')
        general_info_frame.grid(row = 0, column= 0)
        
        measurement_points_label = ttk.Label(general_info_frame, text="Measurement Points: N/A" ,name="measurement_points_label")
        measurement_points_label.pack(side='top', padx=5, pady = 5)

        grid_size_label = ttk.Label(general_info_frame, text="Grid Size = N/A", name="grid_size_label")
        grid_size_label.pack(side='top', padx=5, pady = 5)

        step_size_label = ttk.Label(general_info_frame, text="Step Size = N/A", name="step_size_label")
        step_size_label.pack(side='top', padx=5, pady = 5)

        time_elapsed_label = ttk.Label(general_info_frame, text="Time Elapsed = N/A", name="time_elapsed_label")
        time_elapsed_label.pack(side='top', padx=5, pady = 5)
    
        time_estimated_label = ttk.Label(general_info_frame, text="Time Estimated = N/A", name="time_estimated_label")
        time_estimated_label.pack(side='top', padx=5, pady = 5)   

        # Laser info
        laser_info_frame = tk.LabelFrame(measurement_info_frame, text = "Laser", name = 'laser_info_frame')
        laser_info_frame.grid(row = 0, column = 1, rowspan= 2)

        w_0_label = ttk.Label(laser_info_frame, text="w_0 = N/A", name="w_0_label")
        w_0_label.pack(side='top', padx=5, pady = 5)

        wavelength = ttk.Label(laser_info_frame, text="Wavelength = N/A", name="wavelength")
        wavelength.pack(side='top', padx=5, pady = 5)

        i_0_label = ttk.Label(laser_info_frame, text="I_0 = N/A", name="i_0_label")
        i_0_label.pack(side='top', padx=5, pady = 5)

        z_r_label = ttk.Label(laser_info_frame, text="z_r = N/A", name="z_r_label")
        z_r_label.pack(side='top', padx=5, pady = 5)

        pitch_label = ttk.Label(laser_info_frame, text="Pitch = N/A", name="pitch_label")
        pitch_label.pack(side='top', padx=5, pady = 5)

        yaw_label = ttk.Label(laser_info_frame, text="Yaw = N/A", name="yaw_label")
        yaw_label.pack(side='top', padx=5, pady = 5)

        # Probe info
        probe_info_frame = tk.LabelFrame(measurement_info_frame, text='Probe', name = 'probe_info_frame')
        probe_info_frame.grid(row = 1, column = 0)

        probe_position_label = ttk.Label(probe_info_frame, text="Probe Position = N/A", name="probe_position_label")
        probe_position_label.pack(side='top', padx=5, pady = 5)

        distance_to_sensor_label = ttk.Label(probe_info_frame, text="Distance to Sensor = N/A", name="distance_to_sensor_label")
        distance_to_sensor_label.pack(side='top', padx=5, pady = 5)
    def create_path_plot_frame(self, parent):
        path_plot_frame = tk.LabelFrame(parent, text="Path", name="path_plot_frame")
        

        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        canvas = FigureCanvasTkAgg(fig, master=path_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        path_plot_frame.canvas = canvas
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Path')
        ax.grid(True)
    def create_trajectory_plot_frame(self, parent):
        trajectory_plot_frame = tk.LabelFrame(parent, text="Trajectory", name="trajectory_plot_frame")

        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=trajectory_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        trajectory_plot_frame.canvas = canvas

    # Update Functions
    def update_tab(self, event=None):   
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        data = tab.data

        subtab_group = tab.nametowidget("subtab_group")
        sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")

        measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
        self.current_measurement_id = str(measurement_slider.get())

        self.update_sensor_info_frame()
        self.update_path_plot()

        if data['Visualization']["Slices"] != {}:
            self.update_slice_plot()



        #self.log_event("Updated Tab: " + str(tab_name))
    def update_measurement_info_frame(self):
        
        # update labels here
        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)
        data = tab.data
        subtab_group = tab.nametowidget("subtab_group")
        measurement_info_frame = subtab_group.nametowidget("measurement_info_frame")

        general_info_frame = measurement_info_frame.nametowidget("general_info_frame")
        measurement_points_label = general_info_frame.nametowidget("measurement_points_label")
        grid_size_label = general_info_frame.nametowidget("grid_size_label")
        step_size_label = general_info_frame.nametowidget("step_size_label")
        time_elapsed_label = general_info_frame.nametowidget("time_elapsed_label")
        time_estimated_label = general_info_frame.nametowidget("time_estimated_label")

        measurement_points_label.config(text=f"Measurement Points: {data['3D']['measurement_points']}")
        step_size_label.config(text=f"Step Size: {data['3D']['step_size']}")
        grid_size_label.config(text=f"Grid Size: {data['3D']['grid_size']}")
        time_elapsed_label.config(text=f"Time Elapsed: {data['info']['elapsed_time']}")
        time_estimated_label.config(text=f"Time Estimated: {data['info']['time_estimated']}")

        laser_info_frame = measurement_info_frame.nametowidget("laser_info_frame")
        w_0_label = laser_info_frame.nametowidget("w_0_label")
        wavelength_label = laser_info_frame.nametowidget("wavelength")
        i_0_label = laser_info_frame.nametowidget("i_0_label")
        z_r_label = laser_info_frame.nametowidget("z_r_label")
        pitch_label = laser_info_frame.nametowidget("pitch_label")
        yaw_label = laser_info_frame.nametowidget("yaw_label")
        ''' TODO implement
        w_0_label.config(text=f"w_0: {data['Beam_Parameters']['w_0']:.2f}")
        wavelength_label.config(text="Wavelength: " + str(data['Beam_Parameters']['wavelength']))
        i_0_label.config(text="I_0: " + str(data['Beam_Parameters']['i_0']))
        z_r_label.config(text="z_r: " + str(data['Beam_Parameters']['z_r']))
        '''
        pitch_label.config(text=f"Pitch: {data['Visualization']['Beam_Models']['Measured_Beam']['alpha']:.2f}")
        yaw_label.config(text=f"Yaw: {data['Visualization']['Beam_Models']['Measured_Beam']['beta']:.2f}")


    def update_progress_bar(self, progress_bar, measurements_done):
        
        progress_bar["value"] = measurements_done
        progress_bar.update_idletasks()
    def update_sensor_info_frame(self):
        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)
        data = tab.data

        subtab_group = tab.nametowidget("subtab_group")
        sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
        sensor_info_frame = sensor_path_frame.nametowidget("sensor_info_frame")
        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")

        current_measurement_data = data["Measurements"][self.current_measurement_id]

        sensor_info_frame.config(text="Measurement " + str(self.current_measurement_id) + "/" + str(self.measurement_points)) # Update the title



        # Update the sensor readings
        xpos_label = sensor_readings_frame.nametowidget("xpos_label")
        ypos_label = sensor_readings_frame.nametowidget("ypos_label")
        xdiff_label = sensor_readings_frame.nametowidget("xdiff_label")
        ydiff_label = sensor_readings_frame.nametowidget("ydiff_label")
        sum_label = sensor_readings_frame.nametowidget("sum_label")

        xpos_label.config(text=f"X Position: {current_measurement_data['Signal_xpos']:.2f}")
        ypos_label.config(text=f"Y Position: {current_measurement_data['Signal_ypos']:.2f}")
        xdiff_label.config(text=f"X Diff: {current_measurement_data['Signal_xdiff']:.2f}")
        ydiff_label.config(text=f"Y Diff: {current_measurement_data['Signal_ydiff']:.2f}")
        sum_label.config(text=f"Sum: {current_measurement_data['Signal_sum']:.2f}")

        # Plot the x pos and y pos in sensor_plot_frame
        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        canvas = sensor_plot_frame.canvas 
        ax = canvas.figure.axes[0]
        #ax.clear() #TODO better updating


        # Initialize the plot if it hasn't been initialized yet
        if not hasattr(tab, 'current_point'):
            
            tab.current_point, = ax.plot([], [], 'o', color='red')
        else:
            # Plot the current point in red
            current_x = current_measurement_data['Signal_xpos']
            current_y = current_measurement_data['Signal_ypos']
            tab.current_point.set_data([current_x], [current_y])


        

        sensor_plot_frame.canvas.draw()

        #self.log_event(f"Updated sensor info for Tab {tab}")
    def update_slice_plot(self, event=None):
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)

        data = tab.data 

        subtab_group = tab.nametowidget("subtab_group")
        results_frame = subtab_group.nametowidget("results_frame")
        slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
        vertical_plot_frame = slice_plot_frame.nametowidget("vertical_plot_frame")

        canvas = vertical_plot_frame.canvas
        ax = canvas.figure.axes[0]

        vertical_slice_slider = slice_plot_frame.nametowidget("vertical_slice_slider")
        interpolation_checkbox = slice_plot_frame.nametowidget("interpolation_checkbox")

        interpolation_var = interpolation_checkbox.value.get()
        interpolation = interpolation_var

        slice_index = vertical_slice_slider.get() 

        #only update if data is available
        if data["Visualization"] != {}:
            
            # Update the vertical slice plot
            vertical_slice= data['Visualization']["Slices"]['vertical'][str(slice_index)] # Get the slice data
            heatmap = vertical_slice['heatmap']
            keys = data['Visualization']['Slices']['vertical'].keys()
            first_key = next(iter(keys))
            extent = data['Visualization']['Slices']['vertical'][first_key]['heatmap_extent']

            # Interpolation Method with checkbox
            interpolation_method = 'nearest' if interpolation_var == 0 else 'gaussian'

            # Update the slice plot
            ax.clear()

            cax = ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
            fig = ax.get_figure()

            # Plot colorbar once
            if not hasattr(vertical_plot_frame, 'check'):
                vertical_plot_frame.check = True
                fig.colorbar(cax, ax=ax, label='Signal Sum')
            
            canvas.draw()

            # Update the horizontal slice plot
            horizontal_plot_frame = slice_plot_frame.nametowidget("horizontal_plot_frame")
            canvas = horizontal_plot_frame.canvas
            ax = canvas.figure.axes[0]

            horizontal_slice_slider = slice_plot_frame.nametowidget("horizontal_slice_slider")
            horizontal_slice_index = horizontal_slice_slider.get()

            horizontal_slice = data['Visualization']["Slices"]['horizontal'][str(horizontal_slice_index)] # Get the slice data
            heatmap = horizontal_slice['heatmap']
            extent = data['Visualization']['Slices']['horizontal'][str(horizontal_slice_index)]['heatmap_extent']

            # Update the horizontal slice plot
            ax.clear()
            cax = ax.imshow(heatmap,extent=extent, cmap='hot', interpolation=interpolation_method)
            fig = ax.get_figure()

            # Plot colorbar once
            if not hasattr(horizontal_plot_frame, 'check'):
                horizontal_plot_frame.check = True
                fig.colorbar(cax, ax=ax, label='Signal Sum')

            canvas.draw()

            # Update Beam Plot for Seethrough Planes
            self.update_beam_plot()

        else:
            self.log_event("No Slice Data available")
    def update_beam_plot(self, event = None):
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        data = tab.data

        subtab_group = tab.nametowidget("subtab_group")
        results_frame = subtab_group.nametowidget("results_frame")
        beam_plot_frame = results_frame.nametowidget("beam_plot_frame")

        canvas = beam_plot_frame.canvas
        ax = canvas.figure.axes[0]

        # Update the beam plot
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Beam Plot')
        grid_size = data['3D']['grid_size']
        ax.set_xlim(-grid_size[0],0)
        ax.set_ylim(-grid_size[1]/2, grid_size[1]/2)
        ax.set_zlim(-grid_size[2]/2, grid_size[2]/2)

        ax.set_box_aspect([grid_size[1], grid_size[1], grid_size[2]])

        # Plot the seethrough planes
        # get slider values
        results_frame = subtab_group.nametowidget("results_frame")
        slice_plot_frame = results_frame.nametowidget("slice_plot_frame")
        vertical_slice_slider = slice_plot_frame.nametowidget("vertical_slice_slider")
        horizontal_slice_slider = slice_plot_frame.nametowidget("horizontal_slice_slider")

        vertical_index = str(int(vertical_slice_slider.get()))
        horizontal_index = str(int(horizontal_slice_slider.get()))

        # Extract coords
        vertical_key = str(int(data['Visualization']['Slices']['vertical'][vertical_index]['measurement_ids'][0])) # first Measurement
        horizontal_key = str(int(data['Visualization']['Slices']['horizontal'][horizontal_index]['measurement_ids'][0]))
        x_coord = data['Measurements'][vertical_key]['Measurement_point'][0]
        y_coord = data['Measurements'][horizontal_key]['Measurement_point'][2]
        # TODO check correct coords

        # Plot the planes
        # Create meshgrid for planes
        y = np.linspace(-grid_size[1] / 2, grid_size[1] / 2, 10)
        z = np.linspace(-grid_size[2] / 2, grid_size[2] / 2, 10)
        Y, Z = np.meshgrid(y, z)

        # Vertical plane at x_coord
        X_vertical = np.full_like(Y, x_coord)
        ax.plot_surface(X_vertical, Y, Z, color='cyan', alpha=0.2, edgecolor='none')

        # Horizontal plane at y_coord
        x = np.linspace(-grid_size[0], 0, 10)
        X, Z = np.meshgrid(x, z)
        Y_horizontal = np.full_like(X, y_coord)
        ax.plot_surface(X, Y_horizontal, Z, color='magenta', alpha=0.2, edgecolor='none')


        # Plot the beam
        all_beam_points = data['Visualization']['Beam_Models']['Measured_Beam']['beam_points']
        hull_simplices = data['Visualization']['Beam_Models']['Measured_Beam']['hull_simplices']
        if hull_simplices is not None:
                ax.plot_trisurf(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], triangles=hull_simplices, color='cyan', alpha=0.5, edgecolor='black', label='Convex Hull')
        ax.legend()
        canvas.draw()
    def update_trajectory_plot(self, event = None):
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        data = tab.data

        subtab_group = tab.nametowidget("subtab_group")
        results_frame = subtab_group.nametowidget("results_frame")
        trajectory_plot_frame = results_frame.nametowidget("trajectory_plot_frame")

        canvas = trajectory_plot_frame.canvas
        ax = canvas.figure.axes[0]
        
        plot_alpha_beta(data, ax)
    def update_path_plot(self, event = None):
        tab = self.tab_group.nametowidget(self.tab_group.select())
        data = tab.data
        
        subtab_group = tab.nametowidget("subtab_group")
        sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
        path_plot_frame = sensor_path_frame.nametowidget("path_plot_frame")
        canvas = path_plot_frame.canvas
        ax = canvas.figure.axes[0]

        # Extract the path coordinates from the data
        path = data['3D']['path']
        path_x = path[:int(self.current_measurement_id), 0] # Extract path up to the current measurement
        path_y = path[:int(self.current_measurement_id), 1]
        path_z = path[:int(self.current_measurement_id), 2]

    
        if not hasattr(tab, 'grid_points'):
            X_flat = data['3D']['X'].flatten()
            Y_flat = data['3D']['Y'].flatten()
            Z_flat = data['3D']['Z'].flatten()

            ax.set_xlim(X_flat.min()-0.1, X_flat.max()+0.1)
            ax.set_ylim(Y_flat.min()-0.1, Y_flat.max()+0.1)
            ax.set_zlim(Z_flat.min()-0.1, Z_flat.max()+0.1)

            tab.grid_points = ax.scatter([X_flat], [Y_flat], [Z_flat], color='blue', label='Meshgrid Points',alpha=0.3, s=1)
            #print("Initialized grid points")

        if not hasattr(tab, 'path'):
            tab.path, = ax.plot([], [], [], color='red', label='Path', linewidth = 1)
            ax.legend()
        else:
            tab.path.set_data(path_x, path_y)
            tab.path.set_3d_properties(path_z)

        canvas.draw()

    # Button Functions
    def start_button_pushed(self):
        # TODO close default tab
        # Threading to make interaction with UI possible while measurements are running
        if not self.measurement_running:
            
            if self.simulate_var.get() == 0 and (self.sensor.stage is None or self.hexapod.connection_status == False):
                        self.log_event("Please connect to Hexapod and/or Sensor")
                        return

            self.create_tab()
                        
            self.measurement_running = True
            self.measurement_thread = threading.Thread(target=self.run_measurements)
            self.measurement_thread.start()
            self.log_event("Started Measurements")
        else:
            self.log_event("Measurements already running")
    def save_button_pushed(self):
        #if self.tab_count == 0:
            #self.close_tab(self.tab_group.nametowidget(self.tab_group.select()))


        folder_path = 'C:/Users/Valen/OneDrive/Dokumente/uni_Dokumente/Classes/WiSe2025/Thesis/Actual Work/data'
        directory = filedialog.askdirectory(initialdir=folder_path, title="Select Directory")

        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        data = tab.data
        if directory:  
            probe_name = self.probe_name_entry.get()
            file_name = save_data(directory, data, probe_name)
            self.log_event(f"Data saved to {file_name}")
    def load_button_pushed(self):
        self.log_event("Loading Data")
        file_path = filedialog.askopenfilename(filetypes=[("hdf5 files", "*.h5")])
        if file_path:
            data = load_data(file_path)
            
            self.create_tab(data)
            self.update_tab()
            self.update_trajectory_plot()
            self.update_measurement_info_frame()

            self.measurement_points = data["3D"]["measurement_points"] # TODO also attach this to tab?
            self.current_measurement_id = 0

            tab_name = self.tab_group.select()
            tab = self.root.nametowidget(tab_name)

            subtab_group = tab.nametowidget("subtab_group")
            sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")

            measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
            measurement_slider.config(to=self.measurement_points)
            measurement_slider.set(self.current_measurement_id+1)


            vertical_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("vertical_slice_slider")
            vertical_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['vertical']), state="normal")
            
            horizontal_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("horizontal_slice_slider")
            horizontal_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['horizontal']), state="normal")

            self.update_beam_plot()
            self.log_event(f"Data loaded from {file_path}")
    def stop_button_pushed(self):
        self.measurement_running = False
        self.hexapod.send_command("stop") # Stop the Hexapod
        self.log_event("Stopped Measurements")

    def add_meta_data(self, data):
        data["camera"] = {
         
            "ret": self.ret,
            "mtx": self.mtx,
            "dist": self.dist,
            "rvecs": self.rvecs,
            "tvecs": self.tvecs
        }

        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)

        data["info"] = {
            "name" : tab_name,
            "time_estimated": self.time_estimated,
            "elapsed_time": self.elapsed_time,
            "start_time": self.start_time
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
        one_measurement_time = 1 # [second] 
        
        grid_size = self.measurement_space_entry.get()
        grid_size = tuple(map(float, grid_size.split(',')))

        step_size = self.step_size_entry.get()
        step_size = tuple(map(float, step_size.split(',')))

       
        measurement_points = int((grid_size[0]+1)/(step_size[0])) * int((grid_size[1]+1)/(step_size[1])) * int((grid_size[2]+1)/(step_size[2]))

        #measurement_points = (grid_size[0]+1) * (grid_size[1]+1) * (grid_size[2]+1) / (step_size[0] * step_size[1] * step_size[2])
        
        self.time_estimated = measurement_points * one_measurement_time
        if int(self.time_estimated) > 60:
            self.time_estimated = str(int(self.time_estimated / 60)) + " [min]"
            
        else :
            self.time_estimated = str(int(self.time_estimated)) + " [s]"

        self.new_measurement_panel.nametowidget("input_frame").nametowidget("time_estimated_label").config(text="est. time: "+self.time_estimated)

        self.log_event(f"Estimated time:  {self.time_estimated}")

    def connect_stage(self):
        self.sensor.initialize_stage() 

        if self.sensor.stage is not None:
            self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("stage_connected").select()
            self.log_event("Stage connected")
    def connect_hexapod(self):
        #TODO implement hexapod connection

        checkbox_panel = self.new_measurement_panel.nametowidget("checkbox_panel")
        connection_frame = checkbox_panel.nametowidget("connection_frame")

        server_ip = connection_frame.nametowidget("ip_entry").get()
        port_1 = int(connection_frame.nametowidget("port_1_entry").get())
        port_2 = int(connection_frame.nametowidget("port_2_entry").get())

        rcv = self.hexapod.connect_sockets(server_ip, port_1, port_2) # TODO change to true default ports
        self.log_event(rcv)

        rcv = self.hexapod.move_to_default_position() # TODO put this somewhere else
        self.log_event(rcv)

        if self.hexapod.connection_status == True:
            self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("hexapod_connected").select()

    def manual_alignment(self, manual_adjust_panel):
        #self.hexapod.move_to_default_position()
        # manual alignment for testing
        x = manual_adjust_panel.nametowidget("hexapod_x_entry").get()
        y = manual_adjust_panel.nametowidget("hexapod_y_entry").get()
        z = manual_adjust_panel.nametowidget("hexapod_z_entry").get()
        U = manual_adjust_panel.nametowidget("hexapod_U_entry").get()
        V = manual_adjust_panel.nametowidget("hexapod_V_entry").get()
        W = manual_adjust_panel.nametowidget("hexapod_W_entry").get()

        if manual_adjust_panel.nametowidget("relative_checkbutton_var") == 1:
            self.hexapod.move((x, y, z, U, V, W), flag = "relative")
        else:
            self.hexapod.move((x, y, z, U, V, W), flag = "absolute") 
        self.log_event("Manual Alignment done")
    def rough_alignment(self):
        #TODO implement rough alignment

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("rough_alignment").select()
        self.log_event("Rough Alignment done")
    def fine_alignment(self):
        fine_alignment(self.sensor, self.hexapod) # imported from another file

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("fine_alignment").select()
        self.log_event("Fine Alignment done")

    def run_measurements(self):
        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)
        data = tab.data


        # Get the grid size and step size
        self.grid_size = self.new_measurement_panel.nametowidget("input_frame").nametowidget("measurement_space_entry").get()
        self.grid_size = tuple(map(float, self.grid_size.split(',')))

        self.step_size = self.new_measurement_panel.nametowidget("input_frame").nametowidget("step_size_entry").get()
        self.step_size = tuple(map(float, self.step_size.split(',')))


        # Get Beam Parameters
        alpha = float(self.alpha_entry.get())
        beta = float(self.beta_entry.get())
        self.gauss_beam.set_Trj(alpha, beta)

        self.gauss_beam.w_0 = float(self.w_0_entry.get())*1e-3
        self.gauss_beam.wavelength = float(self.wavelength_entry.get())*1e-9
        self.gauss_beam.I_0 = float(self.i_0_entry.get())
        

        # Get the Measurment points and path points
        self.path_points, self.grid = generate_snake_path(self.grid_size, self.step_size)
        #self.log_event(f'Path Points: \n {self.path_points}')

        self.add_3D_data(data, self.grid, self.grid_size, self.step_size, self.path_points)
        self.log_event("Added 3D Data")

        self.start_time = time.time()
        self.elapsed_time = 0

        self.add_meta_data(data)

        self.measurement_points = data["3D"]["measurement_points"]

        # Update the UI
        subtab_group = tab.nametowidget("subtab_group")
        sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
        measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
        measurement_slider.config(to=self.measurement_points)

        progress_bar = self.new_measurement_panel.nametowidget("progress_bar")
        progress_bar['maximum'] = self.measurement_points
        
        # Start the measurement
        last_point = (0, 0, 0, 0, 0, 0) # Start at the origin
        

        for i in range(self.measurement_points):
            #self.log_event(f"Measurement {i+1} of {self.measurement_points}")

            # As Path points are absolute, transform them to relative positions
            next_point = (self.path_points[i][0], self.path_points[i][1], self.path_points[i][2], 0, 0, 0) 
            next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
            
            #self.log_event(f"Next Relative Position: {next_relative_position}")
            
            if self.hexapod.connection_status is True:
                self.hexapod.move(next_relative_position, flag = "relative") 

            last_point = next_point # Update the last point

            self.doMeasurement(data, self.sensor, self.hexapod, i)
            self.current_measurement_id = i

            if i > 0: # TODO make this work
                #self.event_log.delete("end-2l", "end-1l")
                #self.event_log.insert("end-1l", f"Performed measurement {i+1} / {self.measurement_points}\n")
                self.log_event(f"Performed measurement {i+1} / {self.measurement_points}")
            else:
                self.log_event(f"Performed measurement {i+1} / {self.measurement_points}")
            

            # update only every ~10% of measurements to save time by not updating the UI every step
            update_interval = self.measurement_points // 10
            if i%update_interval == 0:
                measurement_slider.set(i)
                self.update_tab()
                self.update_progress_bar(progress_bar, i+1)
                self.elapsed_time = int((time.time() - self.start_time)/60)
                data["info"]["elapsed_time"] = self.elapsed_time
                

            self.elapsed_time = int((time.time() - self.start_time)/60)
            data["info"]["elapsed_time"] = self.elapsed_time

        

        measurement_slider.config(state = "normal")
        self.new_measurement_panel.nametowidget("save_button").config(state="normal")
        self.log_event("Done with measurements")     

        if self.hexapod.connection_status is True:
            self.hexapod.move_to_default_position() 
            self.log_event("Moved Hexapod to default position")
            
        self.log_event("Starting data processing")
        self.process_data(data)
        self.log_event(f"Finished data processing")

        # Final Update
        # Set Slider limits
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        subtab_group = tab.nametowidget("subtab_group")
        subtab_group.select(subtab_group.nametowidget("results_frame"))
        


        vertical_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("vertical_slice_slider")
        vertical_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['vertical']), state="normal")

        horizontal_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("horizontal_slice_slider")
        horizontal_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['horizontal']), state="normal")

        measurement_slider.set(self.measurement_points)
        self.update_tab()
        self.update_progress_bar(progress_bar,self.measurement_points)
        self.update_trajectory_plot()
        self.update_beam_plot()
        self.update_measurement_info_frame()

        # autosave data
        if self.autosave_var.get() == 1:
            folder_path = 'C:/Users/mtec/Desktop/Thesis_Misc_Valentin/Git_repository/MtecThesis/experiment_data'
            probe_name = str(self.probe_name_entry.get())
            file_path = save_data(folder_path, data, probe_name)
            self.log_event("Data saved automatically to:" + file_path)

        self.measurement_running = False # end threading
   
    def process_data(self, data):
        self.log_event("Processing data")
        process_slices(data)
        self.log_event("Created Slices and Beam Model")
    

    def doMeasurement(self, data, sensor, hexapod, i):
        # Get the current (theoretical) measurement point
        measurement_point = self.path_points[i]

        # Get the absolute Hexapod position for the measurement point 
        hexapod_position = hexapod.position

        # Get data from the sensor
        
        if self.simulate_var.get() == 1:
            signal = sensor.get_test_signal()

            intensity = self.gauss_beam.get_Intensity(point = measurement_point)
            signal.sum = intensity
        else:
            signal = sensor.get_signal()

        measurement_id_str = str(i+1)  # Convert measurement_id to string
        data["Measurements"][measurement_id_str] = {
            
            'Signal_xpos': signal.xpos,
            'Signal_ypos': signal.ypos,
            'Signal_xdiff': signal.xdiff,
            'Signal_ydiff': signal.ydiff,
            'Signal_sum': signal.sum,

            'Measurement_point': measurement_point,
            'Hexapod_position': hexapod_position
        }

if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()