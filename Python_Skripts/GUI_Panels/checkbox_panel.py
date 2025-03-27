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

        self.camera_connected = tk.Checkbutton(self.frame, text="Camera connected", name="camera_connected", variable=self.checkbox_vars["camera_connected"]) # state="disabled",
        self.camera_calibrated = tk.Checkbutton(self.frame, text="Camera calibrated", name="camera_calibrated", variable=self.checkbox_vars["camera_calibrated"]) # state="disabled",
        self.markers_detected = tk.Checkbutton(self.frame, text="Markers detected", name="markers_detected", variable=self.checkbox_vars["markers_detected"]) # state="disabled",
        self.probe_detected = tk.Checkbutton(self.frame, text="Probe detected", name="probe_detected", variable=self.checkbox_vars["probe_detected"]) # state="disabled",
        self.hexapod_connected = tk.Checkbutton(self.frame, text="Hexapod connected", name="hexapod_connected", variable=self.checkbox_vars["hexapod_connected"]) # state="disabled",
        self.stage_connected = tk.Checkbutton(self.frame, text="Stage connected", name="stage_connected", variable=self.checkbox_vars["stage_connected"]) # state="disabled",

        connect_camera_button = tk.Button(self.frame, text="Connect Camera", command = self.root.camera_object.create_camera)
        open_camera_button = tk.Button(self.frame, text="Open Camera", command = lambda: show_camera_panel(root))
        connect_stage_button = tk.Button(self.frame, text="Connect Stage", command= self.connect_stage)
        connect_hexapod_button = tk.Button(self.frame, text="Connect Hexapod", command= self.connect_hexapod)

        #self.manual_alignment_checkbutton = tk.Checkbutton(self.frame, text="Manual Alignment", name="manual_alignment", variable=root.manual_alignment_var, command = self.grey_out)

        for i in range(9):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        self.camera_connected.grid(row=0, column=0, pady=5, sticky="w")
        self.camera_calibrated.grid(row=1, column=0, pady=5, sticky="w")
        self.markers_detected.grid(row=2, column=0, pady=5, sticky="w")
        self.probe_detected.grid(row=3, column=0, pady=5, sticky="w")
        self.hexapod_connected.grid(row=4, column=0, pady=5, sticky="w")
        self.stage_connected.grid(row=5, column=0, pady=5, sticky="w")

        connect_camera_button.grid(row=0, column=1, pady=5, sticky="w")
        open_camera_button.grid(row=1, column=1, pady=5, sticky="w")
        connect_hexapod_button.grid(row=4, column=1, pady=5, sticky="w")
        connect_stage_button.grid(row=5, column=1, pady=5, sticky="w")


        #self.manual_alignment_checkbutton.grid(row=2, column=1, rowspan=2, pady=5, sticky="w")
        #update_checkboxes(root)

        
        # Threading to update checkboxes
        self.checkbox_update_thread = threading.Thread(target= lambda: update_checkboxes(root))
        self.root.thread_list.append(self.checkbox_update_thread)
        self.checkbox_update_thread.start()
        #root.after(2000, self.checkbox_update_thread.start()) # wait for camera to be created
            
    def grey_out(self, flag = None):

        if flag != None:
            if self.root.simulate_var.get() == True:
                self.camera_connected.config(state="disabled")
                self.camera_calibrated.config(state="disabled")
                self.markers_detected.config(state="disabled")
                self.probe_detected.config(state="disabled")
                self.hexapod_connected.config(state="disabled")
                self.stage_connected.config(state="disabled")

                #self.root.manual_alignment_checkbutton.config(state="disabled")

            else:
                self.camera_connected.config(state="normal")
                self.camera_calibrated.config(state="normal")
                self.markers_detected.config(state="normal")
                self.probe_detected.config(state="normal")
                self.hexapod_connected.config(state="normal")
                self.stage_connected.config(state="normal")
                #self.root.manual_alignment_checkbutton.config(state="normal")
            return

        if self.root.manual_alignment_var.get() == True:
            self.camera_connected.config(state="disabled")
            self.camera_calibrated.config(state="disabled")
            self.markers_detected.config(state="disabled")
            self.probe_detected.config(state="disabled")
        else:
            self.camera_connected.config(state="normal")
            self.camera_calibrated.config(state="normal")
            self.markers_detected.config(state="normal")
            self.probe_detected.config(state="normal")


    def _schedule_callback(self, message):
        self.root.after(10, self.root.log.log_event, message) 

    # Unnecessarily complicated, but i didnt want to pass root to the objects, did it eiter way in the end
    def connect_hexapod(self):
        self.root.log.log_event("Connecting to Hexapod. . .")
        thread = threading.Thread(target= lambda: self.root.hexapod.connect_sockets(callback = lambda message: self._schedule_callback(message)))
        self.root.thread_list.append(thread)
        thread.start()

        #self.root.hexapod.connect_sockets(callback = lambda message: self._schedule_callback(message)) 
        #self.root.hexapod.connect_sockets(callback = lambda message: self.root.after(10, self.root.log.log_event, message))

    def connect_stage(self):
        self.root.log.log_event("Connecting to Stage. . .")
        self.root.sensor.initialize_stage(callback = lambda message: self._schedule_callback(message))
        #self.root.sensor.initialize_stage(callback = lambda message: self.root.after(10, self.root.log.log_event, message)) 
