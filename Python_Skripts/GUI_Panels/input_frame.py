import tkinter as tk
from tkinter import ttk

class Input_Frame:

    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.LabelFrame(parent,text ="New Measurement",name="input_frame")

        self.root.input_frame = self.frame

        self.grid_size = self.root.grid_size
        self.step_size = self.root.step_size
        self.time_estimated = "N/A"



        probe_name_label = tk.Label(self.frame, text="Probe Name:")
        measurement_space_label = tk.Label(self.frame, text="3D Size: [mm]")
        step_size_label = tk.Label(self.frame, text="Step Size: [mm]")
   
        self.probe_name_entry = tk.Entry(self.frame, name="probe_name_entry")
        root.probe_name_entry = self.probe_name_entry
        self.measurement_space_entry = tk.Entry(self.frame, name="measurement_space_entry")
        self.step_size_entry = tk.Entry(self.frame, name="step_size_entry")

        self.seperator = ttk.Separator(self.frame, orient="horizontal")

        self.num_centers_label = tk.Label(self.frame, text="Centers to find:")
        self.center_spacing_label = tk.Label(self.frame, text="Center Spacing [mm]")
        self.initial_search_area_label = tk.Label(self.frame, text="Search Area [mm]")
        self.initial_step_size_label = tk.Label(self.frame, text="Step Size [mm]")
        self.refinement_factor_label = tk.Label(self.frame, text="Refinement Factor")
        self.max_iterations_label = tk.Label(self.frame, text="Max Iterations")

        self.num_centers_entry = tk.Entry(self.frame, name="num_centers_entry")
        self.center_spacing_entry = tk.Entry(self.frame, name="center_spacing_entry")
        self.initial_search_area_entry = tk.Entry(self.frame, name="initial_search_area_entry")
        self.initial_step_size_entry = tk.Entry(self.frame, name="initial_step_size_entry")
        self.refinement_factor_entry = tk.Entry(self.frame, name="refinement_factor_entry")
        self.max_num_iterations_entry = tk.Entry(self.frame, name="max_num_iterations_entry")

        self.seperator2 = ttk.Separator(self.frame, orient="horizontal")

        self.time_estimated_label = tk.Label(self.frame, text="Estimated Time: N/A ", name="time_estimated_label")
        time_estimation_button = tk.Button(self.frame, text="Estimate Time", command=self.estimate_time)

        self.probe_name_entry.insert(0, "Default")
        self.measurement_space_entry.insert(0, f"{self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]}")
        self.step_size_entry.insert(0, f"{self.step_size[0]}, {self.step_size[1]}, {self.step_size[2]}")

        self.num_centers_entry.insert(0, str(self.root.num_centers))
        self.center_spacing_entry.insert(0, str(self.root.center_spacing))
        self.initial_search_area_entry.insert(0, str(self.root.initial_search_area))
        self.initial_step_size_entry.insert(0, str(self.root.initial_step_size))
        self.refinement_factor_entry.insert(0, str(self.root.refinement_factor))
        self.max_num_iterations_entry.insert(0, str(self.root.max_num_iterations))


        for i in range(13):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)


        probe_name_label.grid(row=0, column=0, pady=5, sticky="e")
        measurement_space_label.grid(row=1, column=0, pady=5, sticky="e")
        step_size_label.grid(row=2, column=0, pady=5, sticky="e")
        
        self.seperator.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

        self.num_centers_label.grid(row=4, column=0, pady=5, sticky="e")
        self.center_spacing_label.grid(row=5, column=0, pady=5, sticky="e")
        self.initial_search_area_label.grid(row=6, column=0, pady=5, sticky="e")
        self.initial_step_size_label.grid(row=7, column=0, pady=5, sticky="e")
        self.refinement_factor_label.grid(row=8, column=0, pady=5, sticky="e")
        self.max_iterations_label.grid(row=9, column=0, pady=5, sticky="e")

        self.probe_name_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.measurement_space_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.step_size_entry.grid(row=2, column=1, pady=5, sticky="w")
  
        self.num_centers_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.center_spacing_entry.grid(row=5, column=1, pady=5, sticky="w")
        self.initial_search_area_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.initial_step_size_entry.grid(row=7, column=1, pady=5, sticky="w")
        self.refinement_factor_entry.grid(row=8, column=1, pady=5, sticky="w")
        self.max_num_iterations_entry.grid(row=9, column=1, pady=5, sticky="w")
        
        self.seperator2.grid(row=10, column=0, columnspan=2, pady=5, sticky="ew")
        
        self.time_estimated_label.grid(row=11, column=0, pady=5, sticky="e")
        time_estimation_button.grid(row=11, column=1, pady=5, sticky="w")


    def estimate_time(self):
        one_measurement_time = 0.5 # [second] 
        
        grid_size = self.measurement_space_entry.get()
        grid_size = tuple(map(float, grid_size.split(',')))

        step_size = self.step_size_entry.get()
        step_size = tuple(map(float, step_size.split(',')))

       
        measurement_points = int((grid_size[0]+1)/(step_size[0])) * int((grid_size[1]+1)/(step_size[1])) * int((grid_size[2]+1)/(step_size[2]))

        self.time_estimated = measurement_points * one_measurement_time
        if int(self.time_estimated) > 60:
            self.time_estimated = str(int(self.time_estimated / 60)) + " [min]"
            
        else :
            self.time_estimated = str(int(self.time_estimated)) + " [s]"

        self.time_estimated_label.config(text="est. time: "+self.time_estimated)

        self.root.log.log_event(f"Estimated time:  {self.time_estimated}")
