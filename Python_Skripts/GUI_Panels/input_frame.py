import tkinter as tk
from tkinter import ttk

class Input_Frame:

    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.LabelFrame(parent,text ="New Measurement",name="input_frame")

        self.root.input_frame = self.frame

        self.grid_size = self.root.grid_size
        self.step_size = self.root.step_size
        self.time_estimated = 0


        self.path_input_frame = self.create_path_input_frame(self.frame, self.root)
        self.seperator = ttk.Separator(self.frame, orient="horizontal")
        self.center_search_input_frame = self.create_center_search_input_frame(self.frame, self.root)
        self.seperator2 = ttk.Separator(self.frame, orient="horizontal")
        self.time_estimation_frame = self.create_time_estimation_frame(self.frame, self.root)


        for i in range(5):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.frame.grid_columnconfigure(i, weight=1)


        self.path_input_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        self.seperator.grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        self.center_search_input_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        self.seperator2.grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")
        self.time_estimation_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")


    def create_center_search_input_frame(self, parent, root):
        
        def toggle_refine_inputs():
            if root.center_search_method_var.get() == 'refine':
                self.initial_step_size_label.config(state="normal")
                self.refinement_factor_label.config(state="normal")

                self.initial_step_size_entry.config(state="normal")
                self.refinement_factor_entry.config(state="normal")
                pass
            else:
                self.initial_step_size_label.config(state="disabled")
                self.refinement_factor_label.config(state="disabled")

                self.initial_step_size_entry.config(state="disabled")
                self.refinement_factor_entry.config(state="disabled")
                pass
        
        center_search_input_frame = tk.Frame(parent, name="center_search_input_frame")

        #self.quadrant_search_checkbox = tk.Checkbutton(self.frame, text="Quadrant Search", name="quadrant_search_checkbox", variable=self.root.quadrant_search_var)
        #self.quadrant_search_checkbox.grid(row=12, column=0, columnspan=2, pady=5, sticky="ew")
        root.center_search_method_var = tk.StringVar(value="quadrant") 
        
        self.quadrant_search_radiobutton = ttk.Radiobutton(center_search_input_frame, text="Quadrant Search", name="quadrant_search_radiobutton", variable=root.center_search_method_var, value='quadrant', command= toggle_refine_inputs)
        self.refine_search_radiobutton = ttk.Radiobutton(center_search_input_frame, text="Refine Search", name="center_search_radiobutton", variable=root.center_search_method_var, value='refine', command= toggle_refine_inputs)

        seperator = ttk.Separator(center_search_input_frame, orient="vertical")
        self.seperator2 = ttk.Separator(center_search_input_frame, orient="horizontal")

        self.num_centers_label = tk.Label(center_search_input_frame, text="Centers to find:")
        self.center_spacing_label = tk.Label(center_search_input_frame, text="Center Spacing [mm]")
        self.initial_search_area_label = tk.Label(center_search_input_frame, text="Search Area [mm]")
        self.initial_step_size_label = tk.Label(center_search_input_frame, text="Step Size [mm]", state="disabled")
        self.refinement_factor_label = tk.Label(center_search_input_frame, text="Refinement Factor", state="disabled")
        self.max_iterations_label = tk.Label(center_search_input_frame, text="Max Iterations")

        self.num_centers_entry = tk.Entry(center_search_input_frame, name="num_centers_entry", width=3)
        self.center_spacing_entry = tk.Entry(center_search_input_frame, name="center_spacing_entry", width=3)
        self.initial_search_area_entry = tk.Entry(center_search_input_frame, name="initial_search_area_entry", width=3)
        self.initial_step_size_entry = tk.Entry(center_search_input_frame, name="initial_step_size_entry", width=3)
        self.refinement_factor_entry = tk.Entry(center_search_input_frame, name="refinement_factor_entry", width=3)
        self.max_num_iterations_entry = tk.Entry(center_search_input_frame, name="max_num_iterations_entry", width=3)

        self.num_centers_entry.insert(0, str(self.root.num_centers))
        self.center_spacing_entry.insert(0, str(self.root.center_spacing))
        self.initial_search_area_entry.insert(0, str(self.root.initial_search_area))
        self.initial_step_size_entry.insert(0, str(self.root.initial_step_size))
        self.refinement_factor_entry.insert(0, str(self.root.refinement_factor))
        self.max_num_iterations_entry.insert(0, str(self.root.max_num_iterations))

        self.initial_step_size_entry.config(state="disabled")
        self.refinement_factor_entry.config(state="disabled")



        for i in range(9):
            center_search_input_frame.grid_rowconfigure(i, weight=1)
        for i in range(5):
            center_search_input_frame.grid_columnconfigure(i, weight=1)

        self.quadrant_search_radiobutton.grid(row=0, column=0, columnspan=2, pady=5,padx=5, sticky="ew")
        #seperator.grid(row=0, column=2, rowspan=8, sticky="ns", padx=5)
        self.refine_search_radiobutton.grid(row=0, column=3, columnspan=2, pady=5, padx=5, sticky="ew")
        self.seperator2.grid(row=1, column=0, columnspan=5, pady=5, sticky="ew")

        self.num_centers_label.grid(row=2, column=0, pady=5, sticky="w")
        self.center_spacing_label.grid(row=3, column=0, pady=5, sticky="w")
        self.initial_search_area_label.grid(row=4, column=0, pady=5, sticky="w")
        self.max_iterations_label.grid(row=5, column=0, pady=5, sticky="w")

        self.num_centers_entry.grid(row=2, column=1, pady=5, sticky="w")
        self.center_spacing_entry.grid(row=3, column=1, pady=5, sticky="w")
        self.initial_search_area_entry.grid(row=4, column=1, pady=5, sticky="w")
        self.max_num_iterations_entry.grid(row=5, column=1, pady=5, sticky="w")


        self.initial_step_size_label.grid(row=2, column=3, pady=5, sticky="w")
        self.refinement_factor_label.grid(row=3, column=3, pady=5, sticky="w")

        self.initial_step_size_entry.grid(row=2, column=4, pady=5, sticky="w")
        self.refinement_factor_entry.grid(row=3, column=4, pady=5, sticky="w")
        
        return center_search_input_frame

    def create_path_input_frame(self, parent, root):
        path_input_frame = tk.Frame(parent, name="path_input_frame")

        probe_name_label = tk.Label(path_input_frame, text="Probe Name")
        measurement_space_label = tk.Label(path_input_frame, text="3D Size [mm]")
        step_size_label = tk.Label(path_input_frame, text="Step Size: [mm]")
   
        self.probe_name_entry = tk.Entry(path_input_frame, name="probe_name_entry", width=10)
        root.probe_name_entry = self.probe_name_entry
        self.measurement_space_entry = tk.Entry(path_input_frame, name="measurement_space_entry", width=10)
        self.step_size_entry = tk.Entry(path_input_frame, name="step_size_entry", width=10)

        

        self.probe_name_entry.insert(0, "Default")
        self.measurement_space_entry.insert(0, f"{self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]}")
        self.step_size_entry.insert(0, f"{self.step_size[0]}, {self.step_size[1]}, {self.step_size[2]}")

        seperator = ttk.Separator(path_input_frame, orient="vertical")

        center_search_checkbox = tk.Checkbutton(path_input_frame, text="Center Search", name="center_search_checkbox", variable=root.center_search_var)
        box_measurement = tk.Checkbutton(path_input_frame, text="Measurement", name="box_measurement_checkbox", variable=root.box_measurements_var)
        autosave_checkbox = tk.Checkbutton(path_input_frame, text="Autosave", name="autosave_checkbox", variable=root.autosave_var)

        for i in range(3):
            path_input_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            path_input_frame.grid_columnconfigure(i, weight=1)

        probe_name_label.grid(row=0, column=0, pady=5, sticky="w")
        measurement_space_label.grid(row=1, column=0, pady=5, sticky="w")
        step_size_label.grid(row=2, column=0, pady=5, sticky="w")

        self.probe_name_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.measurement_space_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.step_size_entry.grid(row=2, column=1, pady=5, sticky="w")

        seperator.grid(row=0, column=2, rowspan=3, sticky="ns", padx=5)

        autosave_checkbox.grid(row=0, column=3, pady=5, sticky="w")
        center_search_checkbox.grid(row=1, column=3, pady=5, sticky="w")
        box_measurement.grid(row=2, column=3, pady=5, sticky="w")

        return path_input_frame

    def create_time_estimation_frame(self, parent, root):
       
        def estimate_time(self):
            self.time_estimated = 0

            if root.center_search_var.get() == True:
                self.time_estimated += 120 # [s] # rought estimation for center search

            if root.box_measurements_var.get() == True:
            
                one_measurement_time = 0.5 # [second] 
                
                grid_size = self.measurement_space_entry.get()
                grid_size = tuple(map(float, grid_size.split(',')))

                step_size = self.step_size_entry.get()
                step_size = tuple(map(float, step_size.split(',')))

            
                measurement_points = int((grid_size[0]+1)/(step_size[0])) * int((grid_size[1]+1)/(step_size[1])) * int((grid_size[2]+1)/(step_size[2]))

                self.time_estimated += measurement_points * one_measurement_time


            if int(self.time_estimated) > 60:
                time_estimated_str = str(int(self.time_estimated / 60)) + " [min]"
                
            else :
                time_estimated_str = str(int(self.time_estimated)) + " [s]"

            self.time_estimated_label.config(text="est. time: "+time_estimated_str)

            self.root.log.log_event(f"Estimated time: {time_estimated_str}")



            
        time_estimation_frame = tk.Frame(parent, name="time_estimation_frame")

        self.time_estimated_label = tk.Label(time_estimation_frame, text="Estimated Time: N/A ", name="time_estimated_label")
        time_estimation_button = tk.Button(time_estimation_frame, text="Estimate Time", command=lambda: estimate_time(self))

        self.time_estimated_label.pack(side="top", fill="both", expand=True, pady=5)
        time_estimation_button.pack(side="top", fill="none", expand=True, pady=5)

        return time_estimation_frame
