import tkinter as tk
import threading

from Python_Skripts.GUI_Panels.Panel_Updates.update_checkboxes import update_checkboxes, check_checkboxes
from Python_Skripts.GUI_Panels.Panel_Updates.panel_visibility import *


class CheckboxPanel:
    def __init__(self, parent, root):
        self.root = root

        self.frame = tk.LabelFrame(parent, name="checkbox_panel")

        self.checkbox_vars = {
            "camera_connected": tk.IntVar(),
            "camera_calibrated": tk.IntVar(),
            "markers_detected": tk.IntVar(),
            "probe_detected": tk.IntVar(),
            "hexapod_connected": tk.IntVar(),
            "stage_connected": tk.IntVar()
        }

        root.checkbox_vars = self.checkbox_vars

        camera_connected = tk.Checkbutton(self.frame, text="Camera connected", name="camera_connected", state="disabled", variable=self.checkbox_vars["camera_connected"])
        camera_calibrated = tk.Checkbutton(self.frame, text="Camera calibrated", name="camera_calibrated", state="disabled", variable=self.checkbox_vars["camera_calibrated"])
        markers_detected = tk.Checkbutton(self.frame, text="Markers detected", name="markers_detected", state="disabled", variable=self.checkbox_vars["markers_detected"])
        probe_detected = tk.Checkbutton(self.frame, text="Probe detected", name="probe_detected", state="disabled", variable=self.checkbox_vars["probe_detected"])
        hexapod_connected = tk.Checkbutton(self.frame, text="Hexapod connected", name="hexapod_connected", state="disabled", variable=self.checkbox_vars["hexapod_connected"])
        self.stage_connected = tk.Checkbutton(self.frame, text="Stage connected", name="stage_connected", state="disabled", variable=self.checkbox_vars["stage_connected"])

        connect_camera_button = tk.Button(self.frame, text="Connect Camera", command = self.root.camera_object.create_camera)
        open_camera_button = tk.Button(self.frame, text="Open Camera", command = lambda: show_camera_panel(root))
        connect_stage_button = tk.Button(self.frame, text="Connect Stage", command= self.connect_stage)
        connect_hexapod_button = tk.Button(self.frame, text="Connect Hexapod", command= self.connect_hexapod)
        

        for i in range(9):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        camera_connected.grid(row=0, column=0, pady=5, sticky="w")
        camera_calibrated.grid(row=1, column=0, pady=5, sticky="w")
        markers_detected.grid(row=2, column=0, pady=5, sticky="w")
        probe_detected.grid(row=3, column=0, pady=5, sticky="w")
        hexapod_connected.grid(row=4, column=0, pady=5, sticky="w")
        self.stage_connected.grid(row=5, column=0, pady=5, sticky="w")

        connect_camera_button.grid(row=0, column=1, pady=5, sticky="w")
        open_camera_button.grid(row=1, column=1, pady=5, sticky="w")
        connect_hexapod_button.grid(row=4, column=1, pady=5, sticky="w")
        connect_stage_button.grid(row=5, column=1, pady=5, sticky="w")

        #update_checkboxes(root)

        # Threading to update checkboxes
        self.checkbox_update_thread = threading.Thread(target= lambda: update_checkboxes(root))
        self.root.thread_list.append(self.checkbox_update_thread)
        self.checkbox_update_thread.start()
        


    def _schedule_callback(self, message):
        self.root.after(10, self.root.log.log_event, message) 

    # Unnecessarily complicated, but i didnt want to pass root to the objects, did it eiter way in the end
    def connect_hexapod(self):
        self.root.log.log_event("Connecting to Hexapod. . .")
        self.root.hexapod.connect_sockets(callback = lambda message: self._schedule_callback(message)) 
        #self.root.hexapod.connect_sockets(callback = lambda message: self.root.after(10, self.root.log.log_event, message))

    def connect_stage(self):
        self.root.log.log_event("Connecting to Stage. . .")
        self.root.sensor.initialize_stage(callback = lambda message: self._schedule_callback(message))
        #self.root.sensor.initialize_stage(callback = lambda message: self.root.after(10, self.root.log.log_event, message)) 
