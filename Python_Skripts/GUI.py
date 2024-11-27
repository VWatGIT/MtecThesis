import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pypylon.pylon as pylon
from CaptureIMG import capture_image
from calibrate_camera import calibrate_camera
from Object3D import Sensor, Probe, Hexapod
from CreatePath import generate_grid, generate_snake_path

import os
import h5py
import time

class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Python App")
        self.root.geometry("1600x1000")

        self.tab_count = 0
        #self.tabs = {}

        self.data = {} # Data dictionary
        #implement support for multiple data tabs
        
        self.sensor = Sensor()
        self.probe = Probe()
        self.hexapod = Hexapod()

        # Default values
        self.grid_size = (2, 2, 2) # TODO implement this data structure

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
        self.left_panel = tk.Frame(self.root, width=320) # TODO change this depending on needed menu size
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

        measurement_space_label = tk.Label(self.new_measurement_panel, text="Measurement Space: (x, y, z) [mm]")
        measurement_space_label.grid(row=0, column=0, pady=5)
        self.measurement_space_entry = tk.Entry(self.new_measurement_panel, name = "measurement_space_entry")
        self.measurement_space_entry.grid(row=0, column=1, pady=5)
        self.measurement_space_entry.insert(0, f"({self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]})")
        #TODO extract values from entry field with , seperator


        #Set up inputs for Step Size
        step_size_label = tk.Label(self.new_measurement_panel, text="Step Size:")
        step_size_label.grid(row=1, column=0, pady=5)
        self.step_size_entry = tk.Entry(self.new_measurement_panel)
        self.step_size_entry.grid(row=1, column=1, pady=5)
        self.step_size_entry.insert(0, self.step_size)

        #Set up checkboxes
        checkbox_panel = tk.Frame(self.new_measurement_panel)
        checkbox_panel.grid(row=2, column=1, pady=5)

        for i in range(3):
            checkbox_panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            checkbox_panel.grid_columnconfigure(i, weight=1)

        camera_on = tk.Checkbutton(checkbox_panel, text="Camera ON", name="camera_on", state="disabled")
        camera_on.grid(row=0, column=0, pady=5)

        camera_calibrated = tk.Checkbutton(checkbox_panel, text="Camera Calibrated", name="camera_calibrated", state="disabled") 
        camera_calibrated.grid(row=0, column=1, pady=5)

        sensor_detected = tk.Checkbutton(checkbox_panel, text="Sensor Detected", name="markers_detected", state="disabled")
        sensor_detected.grid(row=1, column=0, pady=5)

        probe_detected = tk.Checkbutton(checkbox_panel, text="Probe Detected", name="probe_detected", state="disabled")
        probe_detected.grid(row=1, column=1, pady=5)

        #Set up Buttons
        start_button = tk.Button(self.new_measurement_panel, text="START", command=self.start_button_pushed)
        start_button.grid(row=4, column=0, pady=5)

        save_button = tk.Button(self.new_measurement_panel, text="SAVE", command=self.save_button_pushed)
        save_button.grid(row=4, column=1, pady=5)

        process_data_button = tk.Button(self.new_measurement_panel, text="Process Data", command=self.process_data)
        process_data_button.grid(row=5, column=0, columnspan=2, pady=5)

        #Set up Spinner for Measurement shown
        self.measurement_spinner_label = tk.Label(self.new_measurement_panel, text="Measurement:")
        self.measurement_spinner_label.grid(row=6, column=0, pady=5)
        self.measurement_spinner = tk.Spinbox(self.new_measurement_panel, from_=1, to=self.measurement_points)
        self.measurement_spinner.grid(row=6, column=1, pady=5)
        self.current_measurement_id = str(self.measurement_spinner.get())

        # Bind the Enter key and mouse button release to the update_tab method
        self.measurement_spinner.bind("<Return>", self.update_tab)
        self.measurement_spinner.bind("<ButtonRelease-1>", self.update_tab)
    def create_load_measurement_panel(self, parent):
        self.load_measurement_panel = tk.Frame(parent)

        load_button = tk.Button(self.load_measurement_panel, text="LOAD", command=self.load_button_pushed)
        load_button.pack(pady=5)

        return_button = tk.Button(self.load_measurement_panel, text="Return", command=self.show_home_panel)
        return_button.pack(pady=5)
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
    def create_camera_settings_frame(self, parent):
        self.camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        toggle_camera_button = tk.Checkbutton(self.camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera)
        toggle_camera_button.pack(side = "top", pady=5)

        drawMarkers_button = tk.Checkbutton(self.camera_settings_frame, text="Draw Markers")
        drawMarkers_button.pack(side = "top",pady=5)
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

        self.crop_button = tk.Button(probe_detection_input_frame, text="Crop Image") # TODO implement crop_image
        self.crop_button.grid(row=2, column=0, columnspan=2,rowspan = 2,pady=5)

        # Get the input from the entry field
        #input_text = entry.get()
        # Split the input text by comma and convert to integers
        #x, y = map(int, input_text.split(','))

        self.threshold_slider_label = tk.Label(probe_detection_input_frame, text="Threshold Value", name="threshold_slider_label") 
        self.threshold_slider_label.grid(row=4, column=0, rowspan=2, pady=5)
        self.threshold_slider = tk.Scale(probe_detection_input_frame, from_=0, to=255, orient="horizontal", name="threshold_slider")
        self.threshold_slider.grid(row=4, column=1, rowspan=2, pady=5)

        probe_detection_input_frame.grid_rowconfigure(3, weight=3) #weight row for gap
        
        self.detect_probe_button = tk.Button(probe_detection_input_frame, text="Detect Probe") # TODO implement detect_probe
        self.detect_probe_button.grid(row=6, column=1, pady=5)

        self.probe_detetection_checkbox = tk.Checkbutton(probe_detection_input_frame, text="Probe Detected", name="probe_detected", state="disabled")
        self.probe_detetection_checkbox.grid(row=6, column=0, pady=5)


    def create_marker_detection_frame(self, parent):
        marker_detection_frame = tk.LabelFrame(parent, text="Marker Detection", name="marker_detection_frame")
        # TODO implement marker detection


    def create_camera_calibration_frame(self, parent):

        self.camera_calibration_frame = tk.LabelFrame(parent, text="Camera Calibration", name="camera_calibration_frame")

        for i in range(3):
            self.camera_calibration_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.camera_calibration_frame.grid_columnconfigure(i, weight=1)

        self.create_calibration_image_frame(self.camera_calibration_frame)

        self.calibration_image_frame = self.camera_calibration_frame.nametowidget("calibration_image_frame")
        self.calibration_image_frame.grid(row=0, column=2, rowspan=3, pady=5, sticky="nsew")
        self.calibration_image_frame.propagate(False)
        self.camera_calibration_frame.columnconfigure(2, weight=20)

        #TODO decide on better grid layout

        checkerboard_size_label = tk.Label(self.camera_calibration_frame, text="Checkerboard Size [mm]: ", name="checkerboard_size_label")
        checkerboard_size_label.grid(row=0, column=0, pady=5, sticky="w")
        self.checkerboard_size_entry = tk.Entry(self.camera_calibration_frame, name="checkerboard_size_entry")
        self.checkerboard_size_entry.grid(row=0, column=1, pady=5)
        self.checkerboard_size_entry.insert(0, self.checkerboard_size)

        checkerboard_corners_label = tk.Label(self.camera_calibration_frame, text="Checkerboard Corners [x,y]: ", name="checkerboard_corners_label")
        checkerboard_corners_label.grid(row=1, column=0, pady=5, sticky="w")
        self.checkerboard_corners_entry = tk.Entry(self.camera_calibration_frame, name="checkerboard_corners_entry")
        self.checkerboard_corners_entry.grid(row=1, column=1, pady=5)
        self.checkerboard_corners_entry.insert(0, f"{self.checkerboard_dimensions[0]},{self.checkerboard_dimensions[1]}")


        self.take_image_button = tk.Button(self.camera_calibration_frame, command=self.take_calibration_image, text="Take Image " + str(len(self.checkerboard_images)+1)) #+ "/" + str(self.checkerboard_image_amount))
        self.take_image_button.grid(row=2, column=0, pady=5)

        self.calibrate_button = tk.Button(self.camera_calibration_frame, text="Calibrate", command=self.calibrate_camera, state="active") # TODO decide on state
        self.calibrate_button.grid(row=2, column=1, pady=5)
    def create_calibration_image_frame(self, parent):
        self.calibration_image_frame = tk.LabelFrame(parent, text="Calibration Images", name="calibration_image_frame")
        
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=self.calibration_image_frame)
        canvas.get_tk_widget().pack(side = "left", fill="both")
        self.calibration_image_frame.canvas = canvas

        # Create initial Default Canvas
        #self.create_calibration_image_canvas(self.calibration_image_frame)
        #self.default_image_frame = self.calibration_image_frame.nametowidget("new_image_frame_"+ str(len(self.checkerboard_images)))

    def take_calibration_image(self):
        #if len(self.checkerboard_images) < self.checkerboard_image_amount:         
        self.camera.Open()
        image = capture_image(self.camera)
        self.camera.Close()
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
        rows = num_images  # subplots layout
        cols = 1

        fig, axs = plt.subplots(rows, cols, figsize=(8, 4 * rows))
        fig.subplots_adjust(hspace=0.2)

        if num_images == 0:
            axs = [axs]

        for i in range(num_images):
            row = i // cols 
            col = i % cols
            if rows > 1: # Handle multiple rows
                ax = axs[row]
            else:
                ax = axs if num_images == 1 else axs[row]
            ax.imshow(self.checkerboard_images[i], cmap='gray')
            ax.set_title(f"Image {i + 1}")

        canvas = self.calibration_image_frame.canvas
        canvas.figure = fig
        canvas.draw()

        self.log_event("Updated Calibration Image: " + "new_image_frame_" + str(num_images - 1))
    def calibrate_camera(self):

        self.log_event("Calibrated Camera")
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
        new_tab = ttk.Frame(self.tab_group, name=f"tab{self.tab_count}")
        self.tab_group.add(new_tab, text=f'Tab {self.tab_count}')
        #self.tabs[self.tab_count] = new_tab

        # Configure the grid layout within the new_tab
        for i in range(2):
            new_tab.grid_columnconfigure(i, weight=1)
        for i in range(1):
            new_tab.grid_rowconfigure(i, weight=1)

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
        self.event_log.config(state='normal')
        self.event_log.insert(tk.END, message + '\n')
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
        for i in range(2):
            sensor_info_frame.grid_rowconfigure(i, weight=1)

        self.create_sensor_readings_frame(sensor_info_frame)
        self.create_sensor_position_frame(sensor_info_frame)
        self.create_sensor_plot_frame(sensor_info_frame)

        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")
        sensor_readings_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        sensor_position_frame = sensor_info_frame.nametowidget("sensor_position_frame")
        sensor_position_frame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)    
    
        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        sensor_plot_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)      
    def create_sensor_readings_frame(self, parent):    

        # Create a LabelFrame for X and Y positions
        sensor_readings_frame = tk.LabelFrame(parent, text="Sensor Readings", name="sensor_readings_frame")
        sensor_readings_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        # Add labels to display X and Y positions within the sensor_readings_frame
        xpos_label = ttk.Label(sensor_readings_frame, text="X Position: N/A", name="xpos_label")
        xpos_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        ypos_label = ttk.Label(sensor_readings_frame, text="Y Position: N/A", name="ypos_label")
        ypos_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        xdiff_label = ttk.Label(sensor_readings_frame, text="X Diff: N/A", name="xdiff_label")
        xdiff_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        ydiff_label = ttk.Label(sensor_readings_frame, text="Y Diff: N/A", name="ydiff_label")
        ydiff_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        sum_label = ttk.Label(sensor_readings_frame, text="Sum: N/A", name="sum_label")
        sum_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
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

        for i in range(1):
            results_frame.grid_columnconfigure(i, weight=1)
        for i in range(3):
            results_frame.grid_rowconfigure(i, weight=1)

        self.create_measurement_info_frame(results_frame)

        measurement_info_frame = results_frame.nametowidget("measurement_info_frame")
        measurement_info_frame.grid(row=3, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)
    def create_measurement_info_frame(self, parent):
        measurement_info_frame = tk.LabelFrame(parent, text="Measurement Info", name="measurement_info_frame")

        # Configure the grid layout within the sensor_info_frame LabelFrame
        for i in range(2):
            measurement_info_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            measurement_info_frame.grid_rowconfigure(i, weight=1)

        label_frame = tk.LabelFrame(measurement_info_frame, text="Measurement Info", name="label_frame")
        label_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        measurement_points_label = ttk.Label(label_frame, text="Measurement Points: N/A" ,name="measurement_points_label")
        measurement_points_label.pack(side="top", pady=5)
        step_size_label = ttk.Label(label_frame, text="Step Size = N/A", name="step_size_label")
        step_size_label.pack(side="top", pady=5)
        time_elapsed_label = ttk.Label(label_frame, text="Time Elapsed = N/A", name="time_elapsed_label")
        time_elapsed_label.pack(side="top", pady=5)
        time_estimated_label = ttk.Label(label_frame, text="Time Estimated = N/A", name="time_estimated_label")
        time_elapsed_label.pack(side="top", pady=5)

        progress_bar = ttk.Progressbar(measurement_info_frame, orient="horizontal", length=200, mode="determinate", name="progress_bar")
        progress_bar.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=10, pady=5)

        self.create_path_plot_frame(measurement_info_frame)
        path_plot_frame = measurement_info_frame.nametowidget("path_plot_frame")
        path_plot_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
    def create_path_plot_frame(self, parent):
        path_plot_frame = tk.LabelFrame(parent, text="Path", name="path_plot_frame")
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        canvas = FigureCanvasTkAgg(fig, master=path_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        path_plot_frame.canvas = canvas
        
        grid_size = [2, 2, 4]  # [mm] # TODO change to refer to UI parameters
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

    def update_tab(self, event=None):    
        tab_name = self.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        self.current_measurement_id = str(int(self.measurement_spinner.get()))

        if tab:
            self.update_measurement_info_frame(tab, self.data)
            self.update_sensor_info_frame(tab, self.data)

        sensor_info_frame = tab.nametowidget("sensor_info_frame")
        sensor_info_frame.config(text="Measurement " + str(self.current_measurement_id) + "/" + str(self.measurement_points)) # Update the title

        self.log_event("Updated Tab: " + str(tab_name))
    def update_measurement_info_frame(self, tab, data):
        
        # update labels here
        results_frame = tab.nametowidget("results_frame")
        measurement_info_frame = results_frame.nametowidget("measurement_info_frame")
        label_frame = measurement_info_frame.nametowidget("label_frame")
        measurement_points_label = label_frame.nametowidget("measurement_points_label")
        step_size_label = label_frame.nametowidget("step_size_label")
        time_elapsed_label = label_frame.nametowidget("time_elapsed_label")
        time_estimated_label = label_frame.nametowidget("time_estimated_label")

        measurement_points_label.config(text=f"Measurement Points: {data['3D']['measurement_points']}")
        step_size_label.config(text=f"Step Size: {data['3D']['step_size']}")
        time_elapsed_label.config(text=f"Time Elapsed: {data['info']['elapsed_time']}")
        time_estimated_label.config(text=f"Time Estimated: {data['info']['time_estimated']}")

        # update progress bar here
        progress_bar = measurement_info_frame.nametowidget("progress_bar")
        progress_bar['maximum'] = self.measurement_points
        self.update_progress_bar(progress_bar, self.current_measurement_id)

        # update path plot here
        path_plot_frame = measurement_info_frame.nametowidget("path_plot_frame")
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

        ax.scatter(X_flat, Y_flat, Z_flat, color='blue', label='Meshgrid Points')
        ax.plot(path_x, path_y, path_z, color='red', label='Path')
        #ax.legend()

        self.log_event(f"Updated measurement info for Tab {self.tab_count}")
    def update_progress_bar(self, progress_bar, measurements_done):
        progress_bar["value"] = measurements_done
        progress_bar.update_idletasks()
    def update_sensor_info_frame(self, tab, data):
            
        sensor_info_frame = tab.nametowidget("sensor_info_frame")
        sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")

        current_measurement_data = data[self.current_measurement_id]

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


        # Plot the x pos and y pos in sensor_plot_frame
        sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
        canvas = sensor_plot_frame.canvas 
        ax = canvas.figure.axes[0]
        ax.clear() #TODO after all dots have been shown, dont clear any more

        # Plot all previous points in black
        for measurement_id in range(1, int(self.current_measurement_id)):
            previous_measurement_data = data[str(measurement_id)]
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

        self.log_event(f"Updated sensor info for Tab {tab}")

    def start_button_pushed(self):
        self.create_tab()
        tab_name = self.tab_group.select()
        tab = self.tab_group.nametowidget(tab_name)
        self.log_event("Start button pushed")

        # Get the Measurment points and path points
        X, Y, Z = generate_grid(self.grid_size, self.step_size)
        self.grid = (X, Y, Z)
        self.path_points = generate_snake_path(X, Y, Z)
        self.add_3D_data(self.data, self.grid, self.grid_size, self.step_size, self.path_points)
         

        self.time_one_measurement = 1 # TODO get this from time between measurements
        self.measurement_points = self.data["3D"]["measurement_points"]
        self.time_estimated = self.measurement_points * self.step_size / self.time_one_measurement
        self.start_time = time.time()
        self.elapsed_time = 0

        self.add_meta_data(self.data)

        for i in range(self.measurement_points):
            self.log_event(f"Measurement {i+1} of {self.measurement_points}")
            #self.hexapod.move() # TODO move Hexapod to next position
            #wait for hexapod to move

            self.doMeasurement(self.data, self.sensor, self.probe, i)
            self.measurement_spinner.delete(0, "end")
            self.measurement_spinner.insert(0, i+1) # Update the spinner to the current measurement
            self.update_tab()
            

            self.elapsed_time = time.time() - self.start_time
            self.data["info"]["elapsed_time"] = self.elapsed_time

        
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

    def doMeasurement(self, data, sensor, probe, i):

        # Simulate a measurement TODO delete or comment this
        signal = sensor.get_test_signal() # TODO replace with sensor.get_readings()

        measurement_id_str = str(i+1)  # Convert measurement_id to string
        data[measurement_id_str] = {
            'Signal_xpos': signal.xpos,
            'Signal_ypos': signal.ypos,
            'Signal_xdiff': signal.xdiff,
            'Signal_ydiff': signal.ydiff,
            'Signal_sum': signal.sum,

            'Sensor_xpos': sensor.xposition,
            'Sensor_ypos': sensor.yposition,
            'Sensor_zpos': sensor.zposition,
            #'Sensor_rotation': sensor.rotation,
            'Probe_xpos': probe.xposition,
            'Probe_ypos': probe.yposition,
            'Probe_zpos': probe.zposition,
            #'Probe_rotation': probe.rotation # TODO decide on implementation
        }
        self.log_event(f"Performed measurement {i+1}")
    def process_data(self, data):
        # Process the data
        self.log_event("Processing data")


if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()