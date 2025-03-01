import tkinter as tk
from tkinter import ttk

from Python_Skripts.GUI_Panels.results_frame import ResultsFrame
from Python_Skripts.GUI_Panels.measurement_info_frame import MeasurementInfoFrame
from Python_Skripts.GUI_Panels.sensor_path_frame import SensorPathFrame

from Python_Skripts.Function_Groups.data_handling import new_data


class TabGroup:
    def __init__(self, parent, root):
        self.root = root
        self.tab_count = 0


        self.tab_group = ttk.Notebook(parent, name="tab_group")
        self.tab_group.pack(side="right", fill="both", expand=True)
        self.root.tab_group = self.tab_group

        """ TODO implement this correctly also make updates independent of tab change
        # Bind the <<NotebookTabChanged>> event
        self.root.tab_group.bind("<<NotebookTabChanged>>", self.on_tab_change)
        """

        # TODO dont create default tab, this is only for testing
        self.create_tab() # Create the Default Tab
    
    def on_tab_change(self, event):
        # currently data is stored in the data of the selected tab
        # this is suboptimal but works for now

        if self.root.measurement_running is True:
            self.root.log.log_event("Measurement Running, Tab Change not allowed")
            self.tab_group.select(self.root.tab_group.index("current"))
          

    def create_tab(self, name = "default", data = None):
        self.tab_count += 1
        
        
        # TODO get Tab name from user
        new_tab = ttk.Frame(self.tab_group, name=f"{name}_{self.tab_count}")
        self.tab_group.add(new_tab, text=name)

        new_tab.measurement_slider_var = tk.IntVar(value=1)
        new_tab.measurement_id_var = tk.IntVar(value=1) # Measurement ID TODO what default value?
        new_tab.current_point_index = 0
        
        new_tab.path_points = None
        new_tab.measurement_points = 1
        # TODO trace path to these values in other functions
        
        
        new_tab.time_estimated = 0
        new_tab.elapsed_time = 0 
       

        


        if data == None:
            new_tab.data = new_data()
            if self.root.simulate_var.get() == 1:
                new_tab.data['Simulation']['active'] = True


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
        results_frame.pack(side="left", fill="both", expand=True)
        measurement_info_frame.pack(side="left", fill="both", expand=True)
        sensor_path_frame.pack(side="left", fill="both", expand=True)
        
        # Add Groups to Subtab
        self.subtab_group.add(sensor_path_frame, text="Measurement")
        self.subtab_group.add(results_frame, text="Results")
        self.subtab_group.add(measurement_info_frame, text="Info")