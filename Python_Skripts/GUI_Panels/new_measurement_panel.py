import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time


from Python_Skripts.Function_Groups.data_handling import save_data
from Python_Skripts.GUI_Panels.Panel_Updates.update_checkboxes import check_checkboxes
from Python_Skripts.GUI_Panels.Panel_Updates.panel_visibility import show_tabgroup
from Python_Skripts.GUI_Panels.input_frame import Input_Frame
from Python_Skripts.GUI_Panels.simulation_frame import Simulation_Frame
from Python_Skripts.GUI_Panels.checkbox_panel import CheckboxPanel

from Python_Skripts.GUI_Panels.Movement_Procedures.combined_procedures import combined_procedures

class NewMeasurementPanel:
    def __init__(self, parent, root):
        self.root = root
        
        self.panel = tk.Frame(parent, name="new_measurement_panel")
        self.root.new_measurement_panel = self.panel

        self.input_frame_object = Input_Frame(self.panel, self.root)
        self.checkbox_panel_object = CheckboxPanel(self.panel, self.root)
        root.checkbox_panel_object = self.checkbox_panel_object
        self.simulation_frame_object = Simulation_Frame(self.panel, self.root)

       
  

        self.input_frame = self.input_frame_object.frame
        self.simulation_frame = self.simulation_frame_object.frame
        self.checkbox_panel = self.checkbox_panel_object.frame
       
        root.skip_center_search_var = tk.IntVar()
        root.autosave_var = tk.IntVar()

        start_button = tk.Button(self.panel, text="START", name="start_button", command=self.start_button_pushed, width = 20, height = 3)
        save_button = tk.Button(self.panel, text="SAVE",name="save_button", command=self.save_button_pushed, width = 20, height =3, state="disabled")
        stop_button = tk.Button(self.panel, text="STOP", name="stop_button", command=self.stop_button_pushed, width = 30, height = 5)
        
        progress_bar = ttk.Progressbar(self.panel, orient="horizontal", length=320, mode="determinate", name="progress_bar")
        
        # Create grid 
        for i in range(10):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.panel.grid_columnconfigure(i, weight=1)

        self.input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=10) 
        self.simulation_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=10)
        self.checkbox_panel.grid(row=2, column=0, columnspan=2, padx= 10, pady=5, sticky="nsew")
        
        start_button.grid(row=4, column=0, padx=10, pady=5, sticky = "w")
        save_button.grid(row=4, column=1, padx=10, pady=5, sticky="e")
        stop_button.grid(row=5, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        progress_bar.grid(row=6, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    def start_button_pushed(self):
        # Threading to make interaction with UI possible while measurements are running
        if not self.root.measurement_running:
            
            if check_checkboxes(self.root) == False:
                return
  
            self.root.tab_group_object.create_tab()
            show_tabgroup(self.root)
            self.root.measurement_running = True

            # Thread for all the hexapod movement procedures
            self.all_procedures_thread = threading.Thread(target=combined_procedures, args=(self.root,))
            self.root.thread_list.append(self.all_procedures_thread)
            self.all_procedures_thread.start()
            
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
        self.root.log.log_event("Terminating Measurements")
        self.root.measurement_running = False
        # Stop the Hexapod Server, needs to be restarted
        rcv = self.root.hexapod.send_command("stop")
        self.root.log.log_event(rcv) 
        # TODO: stop all procedures and return to working ui
        # right now ui has to be closed after stopping measurements



if __name__ == "__main__":
    from Python_Skripts.GUI import UserInterface
    root = tk.Tk()
    ui = UserInterface(root, test_mode=True)
    frame = NewMeasurementPanel(root, root).panel

    frame.pack(side = "top")
    root.mainloop()