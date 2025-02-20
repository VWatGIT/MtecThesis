import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading


from Function_Groups.data_handling import save_data
from Python_Skripts.GUI_Panels.Panel_Updates.panel_visibility import *

class NewMeasurementPanel:
    def __init__(self, parent, root):
        self.root = root
        
        self.panel = tk.Frame(parent, name="new_measurement_panel")
        self.root.new_measurement_panel = self.panel

        self.input_frame_object = input_frame(self.panel, self.root)
        self.checkbox_panel_object = CheckboxPanel(self.panel, self.root)


        self.input_frame = self.input_frame_object.frame
        self.checkbox_panel = self.checkbox_panel_object.frame
        self.connection_frame = ConnectionFrame(self.panel, self.root).frame

        self.autosave_var = tk.IntVar()
        autosave_checkbox = tk.Checkbutton(self.panel, text="Autosave", name="autosave_checkbox", variable=self.autosave_var)
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

        self.input_frame.grid(row=0, column=0, rowspan=2, columnspan=1, sticky="nsew", padx=10, pady=10) 
        self.connection_frame.grid(row = 0, column = 1, rowspan = 2, padx=10, pady=10, sticky="nsew")
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
            
            if self.root.simulate_var.get() == 0 and (self.root.sensor.stage is None or self.root.hexapod.connection_status == False):
                self.root.log.log_event("Please connect to Hexapod and/or Sensor")
                return

            self.create_tab()
                        
            self.measurement_running = True
            self.measurement_thread = threading.Thread(target= run_measurements)
            self.measurement_thread.start()
            self.root.log.log_event("Started Measurements")
        else:
            self.root.log.log_event("Measurements already running")
    
    def save_button_pushed(self):
        folder_path = 'C:/Users/Valen/OneDrive/Dokumente/uni_Dokumente/Classes/WiSe2025/Thesis/Actual Work/data'
        directory = filedialog.askdirectory(initialdir=folder_path, title="Select Directory")

        tab_name = self.root.tab_group.select()
        tab = self.root.nametowidget(tab_name)
        data = tab.data
        if directory:  
            probe_name = self.probe_name_entry.get()
            file_name = save_data(directory, data, probe_name)
            self.log_event(f"Data saved to {file_name}")
    
    def stop_button_pushed(self):
        # TODO fix issues with hexapod not reacting to stop command
        self.root.measurement_running = False
        self.root.hexapod.send_command("stop") # Stop the Hexapod
        self.root.log.log_event("Stopped Measurements")

class CheckboxPanel:
    def __init__(self, parent, root):
        self.root = root

        self.frame = tk.Frame(parent, name="checkbox_panel")


        camera_connected = tk.Checkbutton(self.frame, text="Camera connected", name="camera_connected", state="disabled")
        camera_calibrated = tk.Checkbutton(self.frame, text="Camera calibrated", name="camera_calibrated", state="disabled")
        sensor_detected = tk.Checkbutton(self.frame, text="Sensor detected", name="markers_detected", state="disabled")
        probe_detected = tk.Checkbutton(self.frame, text="Probe detected", name="probe_detected", state="disabled")
        hexapod_connected = tk.Checkbutton(self.frame, text="Hexapod connected", name="hexapod_connected", state="disabled")
        self.stage_connected = tk.Checkbutton(self.frame, text="Stage connected", name="stage_connected", state="disabled")

        open_camera_button = tk.Button(self.frame, text="Open Camera", command = show_camera_panel(root))
        connect_stage_button = tk.Button(self.frame, text="Connect Stage", command=self.connect_stage)
        

                
        for i in range(9):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        camera_connected.grid(row=0, column=0, pady=5, sticky="w")
        camera_calibrated.grid(row=1, column=0, pady=5, sticky="w")
        sensor_detected.grid(row=2, column=0, pady=5, sticky="w")
        probe_detected.grid(row=3, column=0, pady=5, sticky="w")
        hexapod_connected.grid(row=4, column=0, pady=5, sticky="w")
        self.stage_connected.grid(row=5, column=0, pady=5, sticky="w")

        open_camera_button.grid(row=0, column=1, pady=5, sticky="w")
        connect_stage_button.grid(row=5, column=1, pady=5, sticky="w")


    def connect_stage(self):
        self.root.sensor.initialize_stage() 

        if self.root.sensor.stage is not None:
            self.stage_connected.select()
            self.log_event("Stage connected") 

class ConnectionFrame:
    def __init__(self, parent, root):
        self.root = root
        
        self.frame = tk.LabelFrame(parent, name="connection_frame")
        self.frame.grid(row=1, column=1, rowspan=4, sticky="nsew")

        for i in range(3):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        port_1_label = tk.Label(self.frame, text="Port 1:")
        port_2_label = tk.Label(self.frame, text="Port 2:")
        ip_label = tk.Label(self.frame, text="IP:")

        self.port_1_entry = tk.Entry(self.frame, name="port_1_entry")
        self.port_2_entry = tk.Entry(self.frame, name="port_2_entry")
        self.ip_entry = tk.Entry(self.frame, name="ip_entry")

        self.port_1_entry.insert(0, "5464")
        self.port_2_entry.insert(0, "5465")
        self.ip_entry.insert(0, '134.28.45.17') # Default IP

        port_1_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        port_2_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ip_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.port_1_entry.grid(row=0, column=1, padx=5, pady=5)
        self.port_2_entry.grid(row=1, column=1, padx=5, pady=5)
        self.ip_entry.grid(row=2, column=1, padx=5, pady=5)

        connect_hexapod_button = tk.Button(self.frame, text="Connect Hexapod", command=self.connect_hexapod)
        connect_hexapod_button.grid(row=3, column=0, columnspan=2, padx=15, pady=5, sticky="nsew")
    
    def connect_hexapod(self):

        server_ip = self.frame.nametowidget("ip_entry").get()
        port_1 = int(self.frame.nametowidget("port_1_entry").get())
        port_2 = int(self.frame.nametowidget("port_2_entry").get())

        rcv = self.hexapod.connect_sockets(server_ip, port_1, port_2)
        self.root.log.log_event(rcv)

class input_frame:

    def __init__(self, parent, root):
        self.root = root
        self.frame = tk.LabelFrame(parent,text ="New Measurement",name="input_frame")

        self.root.input_frame = self.frame

        self.grid_size = (1, 6, 6) #mm
        self.step_size = (1,1,1) #mm
        self.time_estimated = "N/A"



        probe_name_label = tk.Label(self.frame, text="Probe Name:")
        measurement_space_label = tk.Label(self.frame, text="3D Size: [mm]")
        step_size_label = tk.Label(self.frame, text="Step Size: [mm]")
        self.time_estimated_label = tk.Label(self.frame, text="Estimated Time: N/A ", name="time_estimated_label")
        wavelength_label = tk.Label(self.frame, text="Wavelength [nm]:")
        w_0_label = tk.Label(self.frame, text="Beam Waist [mm]:")
        i_0_label = tk.Label(self.frame, text="I_0 [W/m^2]:")
        alpha_label = tk.Label(self.frame, text="Simulate Pitch [deg]:")
        beta_label = tk.Label(self.frame, text="Simulate Yaw [deg]:")

        self.probe_name_entry = tk.Entry(self.frame, name="probe_name_entry")
        self.measurement_space_entry = tk.Entry(self.frame, name="measurement_space_entry")
        self.step_size_entry = tk.Entry(self.frame, name="step_size_entry")
        self.wavelength_entry = tk.Entry(self.frame, name="wavelength_entry")
        self.w_0_entry = tk.Entry(self.frame, name="w_0_entry")
        self.i_0_entry = tk.Entry(self.frame, name="i_0_entry")
        self.alpha_entry = tk.Entry(self.frame, name="alpha_entry")
        self.beta_entry = tk.Entry(self.frame, name="beta_entry")

        time_estimation_button = tk.Button(self.frame, text="Estimate Time", command=self.estimate_time)

        self.seperator = ttk.Separator(self.frame, orient="horizontal")
        self.simulate_var = tk.IntVar()
        self.root.simulate_var = self.simulate_var # add to root for access in other functions
        self.simulate_checkbox = tk.Checkbutton(self.frame, text="Simulate", name="simulate_checkbox", variable=self.simulate_var)

        self.probe_name_entry.insert(0, "Default")
        self.measurement_space_entry.insert(0, f"{self.grid_size[0]}, {self.grid_size[1]}, {self.grid_size[2]}")
        self.step_size_entry.insert(0, f"{self.step_size[0]}, {self.step_size[1]}, {self.step_size[2]}")
        self.wavelength_entry.insert(0, "1300")
        self.w_0_entry.insert(0, "1")
        self.i_0_entry.insert(0, "60000")
        self.alpha_entry.insert(0, "0")
        self.beta_entry.insert(0, "0")

        for i in range(11):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)


        probe_name_label.grid(row=0, column=0, pady=5, sticky="e")
        measurement_space_label.grid(row=1, column=0, pady=5, sticky="e")
        step_size_label.grid(row=2, column=0, pady=5, sticky="e")
        self.time_estimated_label.grid(row=3, column=0, pady=5, sticky="w")

        self.seperator.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        self.simulate_checkbox.grid(row = 5, column=0, columnspan=2, pady=5, sticky="n")
        
        wavelength_label.grid(row=6, column=0, pady=5, sticky="e")
        w_0_label.grid(row=7, column=0, pady=5, sticky="e")
        i_0_label.grid(row=8, column=0, pady=5, sticky="e")
        alpha_label.grid(row=9, column=0, pady=5, sticky="e")
        beta_label.grid(row=10, column=0, pady=5, sticky="e")

        self.probe_name_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.measurement_space_entry.grid(row=1, column=1, pady=5, sticky="w")
        self.step_size_entry.grid(row=2, column=1, pady=5, sticky="w")

        self.wavelength_entry.grid(row=6, column=1, pady=5, sticky="w")
        self.w_0_entry.grid(row=7, column=1, pady=5, sticky="w")
        self.i_0_entry.grid(row=8, column=1, pady=5, sticky="w")
        self.alpha_entry.grid(row=9, column=1, pady=5, sticky="w")
        self.beta_entry.grid(row=10, column=1, pady=5, sticky="w")

        
        time_estimation_button.grid(row=3, column=1, pady=5, sticky="w")
        

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


if __name__ == "__main__":
    root = tk.Tk()
    # setup root
    
    root.hexapod = None
    root.sensor = None
    root.camera = None
    root.log = None
    root.measurement_running = False


    frame = NewMeasurementPanel(root, root).panel
    frame.pack()
    root.mainloop()