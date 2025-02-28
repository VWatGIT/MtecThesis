import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time


from Python_Skripts.Function_Groups.data_handling import save_data
from Python_Skripts.GUI_Panels.Movement_Procedures.run_measurements import run_measurements
from Python_Skripts.GUI_Panels.Movement_Procedures.find_beam_centers import find_beam_centers
from Python_Skripts.GUI_Panels.Panel_Updates.update_checkboxes import check_checkboxes
from Python_Skripts.GUI_Panels.input_frame import Input_Frame
from Python_Skripts.GUI_Panels.simulation_frame import Simulation_Frame
from Python_Skripts.GUI_Panels.checkbox_panel import CheckboxPanel


class NewMeasurementPanel:
    def __init__(self, parent, root):
        self.root = root
        
        self.panel = tk.Frame(parent, name="new_measurement_panel")
        self.root.new_measurement_panel = self.panel

        self.input_frame_object = Input_Frame(self.panel, self.root)
        self.simulation_frame_object = Simulation_Frame(self.panel, self.root)
        self.checkbox_panel_object = CheckboxPanel(self.panel, self.root)
       
        root.checkbox_panel_object = self.checkbox_panel_object

        self.input_frame = self.input_frame_object.frame
        self.simulation_frame = self.simulation_frame_object.frame
        self.checkbox_panel = self.checkbox_panel_object.frame
       

        root.autosave_var = tk.IntVar()
        autosave_checkbox = tk.Checkbutton(self.panel, text="Autosave", name="autosave_checkbox", variable=self.root.autosave_var)
        #autosave_checkbox.select()

        start_button = tk.Button(self.panel, text="START", name="start_button", command=self.start_button_pushed, width = 20, height = 3)
        save_button = tk.Button(self.panel, text="SAVE",name="save_button", command=self.save_button_pushed, width = 20, height =3, state="disabled")
        stop_button = tk.Button(self.panel, text="STOP", name="stop_button", command=self.stop_button_pushed, width = 30, height = 5)
        
        progress_bar = ttk.Progressbar(self.panel, orient="horizontal", length=320, mode="determinate", name="progress_bar")
        
        # Create grid 
        for i in range(10):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.panel.grid_columnconfigure(i, weight=1)

        self.input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10) 
        self.simulation_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        self.checkbox_panel.grid(row=2, column=0, columnspan=2, padx= 10, pady=5, sticky="nsew")
        
        autosave_checkbox.grid(row=3, column=0, columnspan=2, pady=5, sticky="nsew")
        start_button.grid(row=4, column=0, padx=10, pady=5, sticky = "w")
        save_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        stop_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        progress_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    def start_button_pushed(self):
        # TODO close default tab
        # Threading to make interaction with UI possible while measurements are running
        if not self.root.measurement_running:
            
            if self.root.simulate_var.get() != 1:
                # check checkboxes if everything is ready
                if check_checkboxes(self.root) == False:
                    return
            else:
                self.root.log.log_event("Simulating Measurements")
                

            self.root.tab_group_object.create_tab()    
            self.root.measurement_running = True

            # Move to starting position
            # TODO move to starting position

            self.root.log.log_event("Starting Trajectory Determination")
            centers = find_beam_centers(self.root)

            # Now calculate the trajectory
            self.root.log.log_event("Calculating Trajectory")

            # TODO calculate trajectory

            self.root.log.log_event("Trajectory Determination Finished")

            # Now align the probe with sensor in an angle
            # TODO align probe with sensor again

            # Now start the measurements
            self.root.log.log_event("Started Measurements")
            self.measurement_thread = threading.Thread(target= run_measurements(self.root))
            self.root.thread_list.append(self.measurement_thread)
            root.after(10, self.measurement_thread.start()) # delay to change tab first

        else:
            self.root.log.log_event("Measurements already running")
    
    def save_button_pushed(self):
        folder_path = 'C:/Users/Valen/OneDrive/Dokumente/uni_Dokumente/Classes/WiSe2025/Thesis/Actual Work/data'
        directory = filedialog.askdirectory(initialdir=folder_path, title="Select Directory")

        tab_name = self.root.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        data = tab.data
        if directory:  
            self.root.log.log_event(f"Saving Data")
            probe_name = self.input_frame_object.probe_name_entry.get()
            file_name = save_data(directory, data, probe_name)
            self.root.log.log_event(f"Data saved to {file_name}")
    
    def stop_button_pushed(self):
        # TODO fix issues with hexapod not reacting to stop command
        self.root.measurement_running = False
        self.root.hexapod.send_command("stop") # Stop the Hexapod
        self.root.log.log_event("Terminating Measurements")




if __name__ == "__main__":
    from Python_Skripts.GUI import UserInterface
    root = tk.Tk()
    ui = UserInterface(root, test_mode=True)
    frame = NewMeasurementPanel(root, root).panel

    frame.pack(side = "top")
    root.mainloop()