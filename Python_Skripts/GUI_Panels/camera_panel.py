import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os


from Function_Groups.camera import * 
from Function_Groups.marker_detection import *

from GUI_Panels.camera_calibration_frame import CameraCalibrationFrame
from GUI_Panels.camera_detection_frame import ProbeDetectionFrame, MarkerDetectionFrame

class CameraPanel:
    def __init__(self, parent, root):
        self.camera = root.camera_object.camera
        self.log = root.log
        self.root = root

        
        
        self.camera_calibrated = False
        self.ret, self.mtx, self.dist, self.rvecs, self.tvecs = None , None, None, None , None # Camera Calibration Values


        self.panel = tk.Frame(parent, name="camera_panel") # notebook to save time TODO rename
        self.panel.place(relx=1, rely=1, anchor="center", relheight=1, relwidth=1)

        self.camera_plot_frame = self.create_camera_plot_frame(self.panel)
        self.canvas = self.camera_plot_frame.canvas
        # Attach to Root fore easy access
        self.root.camera_plot_frame = self.camera_plot_frame
        self.root.camera_panel = self.panel

        for i in range(3):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(1):
            self.panel.grid_columnconfigure(i, weight=1)
 
        self.camera_settings_frame = self.create_camera_settings_frame(self.panel)
        
        self.helper_panel = tk.Frame(self.panel)

        # Fill Helper Panel    
        self.camera_calibration_object = CameraCalibrationFrame(self.helper_panel, self.root)
        self.probe_detection_object = ProbeDetectionFrame(self.helper_panel, self.root)
        self.marker_detection_object = MarkerDetectionFrame(self.helper_panel, self.root)

        self.camera_calibration_frame = self.camera_calibration_object.frame
        self.probe_detection_frame = self.probe_detection_object.frame
        self.marker_detection_frame = self.marker_detection_object.frame

        self.camera_calibration_frame.pack(side="left", expand=True)
        self.probe_detection_frame.pack(side="left", expand=True)
        self.marker_detection_frame.pack(side="left", expand=True)

        self.helper_panel.grid(row=0, column=0, sticky="nsew")
        self.camera_plot_frame.grid(row=0, column=1, sticky="nsew")
        self.camera_settings_frame.grid(row=0, column=2, sticky="nsew")
        

        # have camera_helper | camera image | camera settings        
        # TODO fill panel and hide calibration and detection frames until needed

        return_button = tk.Button(self.panel, text="Return", command= lambda: self.panel.place_forget())
        return_button.place(relx=1, rely= 0, anchor="ne")

        

    def create_camera_plot_frame(self, parent):
        camera_plot_frame = tk.LabelFrame(parent, text="Camera Image", name="camera_plot_frame")
        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=camera_plot_frame)
        canvas.get_tk_widget().place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
        camera_plot_frame.canvas = canvas
        ax.axis('off')
        return camera_plot_frame

    def create_camera_settings_frame(self, parent):
        camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        toggle_camera_button = tk.Checkbutton(camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera)
        toggle_camera_button.pack(side = "top", pady=5)
        return camera_settings_frame

    def toggle_camera(self):
        if self.camera.IsOpen():
            self.camera.Close()
        else:
            self.camera.Open()
            self.panel.after(10, self.update_camera())
        self.log.log_event("Toggled Camera")

    def update_camera(self):
        # TODO use same canvas for all functions
        
        if self.camera.IsOpen():
            image = capture_image(self.camera)

            if self.camera_calibrated:
                image, marker_rvecs, marker_tvecs = detect_markers(image, self.mtx, self.dist)

                self.sensor.marker_rvecs = marker_rvecs[self.sensor.marker_id]
                self.sensor.marker_tvecs = marker_tvecs[self.sensor.marker_id]
                self.probe.marker_rvecs = marker_rvecs[self.probe.marker_id]
                self.probe.marker_tvecs = marker_tvecs[self.probe.marker_id]

            # Update Camera Image
            ax = self.canvas.figure.axes[0]
            
            ax.clear()
            ax.imshow(image)
            self.canvas.draw()
            #self.root.after(10, self.update_camera()) #TODO fix bug that crashes UI

if __name__ == "__main__":
    root = tk.Tk()
    root.log = None
    root.probe = None
    root.sensor = None
    root.hexapod = None

    os.environ["PYLON_CAMEMU"] = "1"
    root.camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
    root.camera.Open()

    camera_panel = CameraPanel(root, root)
    camera_panel.panel.pack(side="top", fill="both", expand=True)
     
    root.mainloop()
    root.camera.Close()