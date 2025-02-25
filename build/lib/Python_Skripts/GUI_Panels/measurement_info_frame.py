import tkinter as tk
from tkinter import ttk

class MeasurementInfoFrame:
    def __init__(self, parent, root):
        self.frame = tk.LabelFrame(parent, name="measurement_info_frame") 

        for i in range(2):
            self.frame.rowconfigure(i, weight = 1)
        for i in range(2):
            self.frame.columnconfigure(i, weight = 1)

        # General info 
        general_info_frame = self.create_general_info_frame(self.frame)
        probe_info_frame = self.create_probe_info_frame(self.frame)
        laser_info_frame = self.create_laser_info_frame(self.frame)
        
        general_info_frame.grid(row = 0, column= 0)
        probe_info_frame.grid(row = 1, column = 0)
        laser_info_frame.grid(row = 0, column = 1, rowspan= 2)

    def create_general_info_frame(self, parent):
        general_info_frame = tk.LabelFrame(parent, text = 'Info', name='general_info_frame')

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
        return general_info_frame
    
    def create_laser_info_frame(self, parent):
        # Laser info
        laser_info_frame = tk.LabelFrame(parent, text = "Laser", name = 'laser_info_frame')
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

        return laser_info_frame


    def create_probe_info_frame(self, parent):
        probe_info_frame = tk.LabelFrame(self.frame, text='Probe', name = 'probe_info_frame')

        probe_position_label = ttk.Label(probe_info_frame, text="Probe Position = N/A", name="probe_position_label")
        probe_position_label.pack(side='top', padx=5, pady = 5)

        distance_to_sensor_label = ttk.Label(probe_info_frame, text="Distance to Sensor = N/A", name="distance_to_sensor_label")
        distance_to_sensor_label.pack(side='top', padx=5, pady = 5)

        return probe_info_frame