import tkinter as tk
from tkinter import ttk

from GUI_Panels.results_frame import ResultsFrame
from GUI_Panels.measurement_info_frame import MeasurementInfoFrame
from GUI_Panels.sensor_path_frame import SensorPathFrame

from Function_Groups.data_handling import new_data


class TabGroup:
    def __init__(self, parent, root):
        self.root = root
        self.tab_count = 0


        self.tab_group = ttk.Notebook(parent, name="tab_group")
        self.tab_group.pack(side="right", fill="both", expand=True)

        self.root.tab_group = self.tab_group

        self.create_tab() # Create the Default Tab
   
    def create_tab(self, name = "default", data = None):
        self.tab_count += 1
        
        # TODO get Tab name from user
        new_tab = ttk.Frame(self.tab_group, name=f"{name}_{self.tab_count}")
        self.tab_group.add(new_tab, text=name)
        

        # TODO trace path to these values in other functions
        new_tab.measurement_points = 1
        new_tab.time_estimated = 0
        new_tab.elapsed_time = 0 
        new_tab.current_measurement_id = 0

        


        if data == None:
            new_tab.data = new_data()
        else:
            new_tab.data = data 

        self.create_subtabs(new_tab)

        close_button = tk.Button(new_tab, text="Close Tab", command=lambda: self.close_tab(new_tab), name="close_button") # create this last in create_tab
        close_button.place(relx=1, rely=0, anchor="ne")  # Place the close button in the top-right corner

        self.tab_group.select(new_tab)

        # Log the creation of a new tab
        self.root.log.log_event(f"Created Tab {self.tab_count}") 
        
    def close_tab(self, tab):
        self.tab_group.forget(tab)
        self.root.log.log_event(f"Closed Tab {self.tab_count}")
        self.tab_count -= 1

    def create_subtabs(self, parent):
        self.subtab_group = ttk.Notebook(parent, name="subtab_group")
        self.subtab_group.pack(side="right", fill="both", expand=True)

        #Create Frames
        results_frame = ResultsFrame(self.subtab_group, self.root).frame
        measurement_info_frame = MeasurementInfoFrame(self.subtab_group, self.root).frame
        sensor_path_frame = SensorPathFrame(self.subtab_group, self.root).frame

        # Pack Frames
        results_frame.pack(side="right", fill="both", expand=True)
        measurement_info_frame.pack(side="right", fill="both", expand=True)
        sensor_path_frame.pack(side="right", fill="both", expand=True)
        
        # Add Groups to Subtab
        self.subtab_group.add(sensor_path_frame, text="Measurement")
        self.subtab_group.add(results_frame, text="Results")
        self.subtab_group.add(measurement_info_frame, text="Info")