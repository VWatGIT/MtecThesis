import tkinter as tk

from Function_Groups.camera import * 
from Function_Groups.marker_detection import *

from GUI_Panels.camera_calibration_frame import CameraCalibrationFrame
from GUI_Panels.camera_detection_frame import ProbeDetectionFrame, MarkerDetectionFrame

from Function_Groups.probe_tip_detection import draw_probe_tip



class CameraPanel:
    def __init__(self, parent, root):
        self.camera = root.camera_object.camera
        self.log = root.log
        self.root = root


        self.panel = tk.Frame(parent, name="camera_panel") # notebook to save time TODO rename
        self.panel.place(relx=1, rely=1, anchor="center", relheight=1, relwidth=1)

        self.camera_plot_frame = self.create_camera_plot_frame(self.panel)
        self.canvas = self.camera_plot_frame.canvas
        # Attach to Root fore easy access
        self.root.camera_plot_frame = self.camera_plot_frame
        self.root.camera_panel = self.panel

        for i in range(0):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(3):
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

        self.camera_calibration_frame.pack(side="top", expand=True)
        self.probe_detection_frame.pack(side="top", expand=True)
        self.marker_detection_frame.pack(side="top", expand=True)

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
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
        canvas = FigureCanvasTkAgg(fig, master=camera_plot_frame)
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        camera_plot_frame.canvas = canvas
        ax.axis('off')
        ax.set_aspect('equal')
        return camera_plot_frame

    def create_camera_settings_frame(self, parent):
        camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        
        self.draw_markers_var = tk.IntVar()
        self.draw_probe_tip_var = tk.IntVar()

        toggle_camera_checkbutton = tk.Checkbutton(camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera)
        draw_markers_checkbutton = tk.Checkbutton(camera_settings_frame, text="Draw Markers", command= self.update_camera, variable= self.draw_markers_var)
        draw_probe_tip_checkbutton = tk.Checkbutton(camera_settings_frame, text="Draw Probe Tip", command=self.update_camera, variable= self.draw_probe_tip_var)

        toggle_camera_checkbutton.pack(side = "top", pady=5)
        draw_markers_checkbutton.pack(side = "top", pady=5)
        draw_probe_tip_checkbutton.pack(side = "top", pady=5)

        return camera_settings_frame

    def toggle_camera(self):
        if self.camera.IsOpen():
            self.camera.Close()
            self.camera_plot_frame.canvas.figure.axes[0].clear()
            self.camera_plot_frame.canvas.draw()
        else:
            self.camera.Open()
            self.panel.after(10, self.update_camera())
        #self.log.log_event(str(self.camera.IsOpen()))
        self.log.log_event("Toggled Camera")

    def update_camera(self):
        # TODO use same canvas for all functions
        
        if self.camera.IsOpen():
            image = capture_image(self.camera)

            if self.root.camera_object.camera_calibrated:
                
                if self.draw_markers_var == 1:

                    mtx = self.root.camera_object.mtx
                    dist = self.root.camera_object.dist
                    sensor_marker_size = self.root.sensor.marker_size
                    probe_marker_size = self.root.probe.marker_size 

                    marker_size = sensor_marker_size # for now assume same size TODO implement different sizes
                    
                    # marker drawn in detect markers
                    image, marker_rvecs, marker_tvecs = detect_markers(image, marker_size, mtx, dist)


                    if marker_rvecs != [] and marker_tvecs != []:
                        self.sensor.marker_rvecs = marker_rvecs[self.sensor.marker_id]
                        self.sensor.marker_tvecs = marker_tvecs[self.sensor.marker_id]
                        self.probe.marker_rvecs = marker_rvecs[self.probe.marker_id]
                        self.probe.marker_tvecs = marker_tvecs[self.probe.marker_id]
                
                    if self.draw_probe_tip_var == 1:
                        image = draw_probe_tip(image, self.root.probe.probe_tip_position_in_camera_image)


            # Update Camera Image
            ax = self.canvas.figure.axes[0]
            
            ax.clear()
            ax.imshow(image)
            self.canvas.draw()
            

if __name__ == "__main__":
    from GUI_Panels.event_log_panel import EventLogPanel
    from Function_Groups.object3D import *

    root = tk.Tk()
    root.log = EventLogPanel(root, root)
    root.probe = Probe()
    root.sensor = Sensor()
    root.hexapod = Hexapod()

    root.camera_object = Camera()
    root.camera = root.camera_object.camera

    path = r"C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\misc\Aruco-markers-4x4-50.png"
    root.camera_object.set_emulated_image(path)

    camera_panel = CameraPanel(root, root)
    camera_panel.panel.pack(side="top", fill="both", expand=True)
    root.log.panel.pack(side="bottom", fill="x", expand=True)

    root.mainloop()
    root.camera.Close()