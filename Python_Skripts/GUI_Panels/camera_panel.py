import tkinter as tk
import threading
import time
    

from Python_Skripts.Function_Groups.camera import * 
from Python_Skripts.Function_Groups.marker_detection import *

from Python_Skripts.GUI_Panels.camera_calibration_frame import CameraCalibrationFrame
from Python_Skripts.GUI_Panels.camera_detection_frame import ProbeDetectionFrame, MarkerDetectionFrame
from Python_Skripts.GUI_Panels.manual_adjust_panel import ManualAdjustPanel

from Python_Skripts.GUI_Panels.Panel_Updates.update_camera import update_camera, zoom


class CameraPanel:
    def __init__(self, parent, root):
        self.camera_object = root.camera_object
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

        

        for i in range(1):
            self.panel.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.panel.grid_columnconfigure(i, weight=1)
 
        
        
        self.helper_panel = tk.Frame(self.panel)

        # Fill Helper Panel    
        self.camera_calibration_object = CameraCalibrationFrame(self.helper_panel, self.root)
        self.probe_detection_object = ProbeDetectionFrame(self.helper_panel, self.root)
        self.marker_detection_object = MarkerDetectionFrame(self.helper_panel, self.root)
        self.manual_adjust_panel_object = ManualAdjustPanel(self.helper_panel, self.root)

        # attach object to root
        self.root.camera_calibration_object = self.camera_calibration_object

        self.camera_settings_frame = self.create_camera_settings_frame(self.helper_panel)
        self.camera_calibration_frame = self.camera_calibration_object.frame
        self.probe_detection_frame = self.probe_detection_object.frame
        self.marker_detection_frame = self.marker_detection_object.frame
        self.manual_adjust_panel = self.manual_adjust_panel_object.panel
        
        self.camera_settings_frame.pack(side="top", fill="both", expand=True)
        self.camera_calibration_frame.pack(side="top", fill="both", expand=True)
        self.probe_detection_frame.pack(side="top", fill="both",expand=True)
        self.marker_detection_frame.pack(side="top", fill="both",expand=True)
        self.manual_adjust_panel.pack(side="top", fill="both", expand=True)

        # camera_helper | camera image
        self.helper_panel.grid(row=0, column=0, sticky="ns")
        self.camera_plot_frame.grid(row=0, column=1, sticky="nsew")

        self.panel.grid_columnconfigure(1, weight=100)
               
        return_button = tk.Button(self.panel, text="Return", command= lambda: self.panel.place_forget())
        return_button.place(relx=1, rely= 0, anchor="ne")

        self.toggle_camera()


    def create_camera_plot_frame(self, parent):
        camera_plot_frame = tk.LabelFrame(parent, text="Camera Image", name="camera_plot_frame")
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
        canvas = FigureCanvasTkAgg(fig, master=camera_plot_frame)
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        camera_plot_frame.canvas = canvas
        
        canvas.mpl_connect('button_press_event', self._on_click)
        canvas.mpl_connect('scroll_event', lambda event: zoom(event, ax, self.camera_object.original_xlim, self.camera_object.original_ylim))

        ax.axis('off')
        ax.set_aspect('equal')
        return camera_plot_frame


    def _on_click(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata

            # Store the clicked position in the probe object
            self.root.probe.probe_tip_position_in_camera_image = (int(x), int(y))

            self.root.log.log_event(f"Set Probe Tip in Camera Image to : ({int(x)}, {int(y)})")
        
    


    def create_camera_settings_frame(self, parent):
        camera_settings_frame = tk.LabelFrame(parent, text="Camera Settings", name="camera_settings_frame")
        
        self.root.toggle_camera_var = tk.IntVar(value=0)
        self.root.draw_markers_var = tk.IntVar(value=0)
        self.root.draw_probe_tip_var = tk.IntVar(value=1)
        self.root.draw_checkerboard_var = tk.IntVar(value=0)

        toggle_camera_checkbutton = tk.Checkbutton(camera_settings_frame, text="Camera ON/OFF", command=self.toggle_camera, variable= self.root.toggle_camera_var)
        draw_markers_checkbutton = tk.Checkbutton(camera_settings_frame, text="Draw Markers",  variable= self.root.draw_markers_var)
        draw_probe_tip_checkbutton = tk.Checkbutton(camera_settings_frame, text="Draw Probe Tip", variable= self.root.draw_probe_tip_var)
        draw_checkerboard_checkbutton = tk.Checkbutton(camera_settings_frame, text="Draw Checkerboard", variable= self.root.draw_checkerboard_var)

        connect_camera_button = tk.Button(camera_settings_frame, text="Connect Camera", command = self.camera_object.create_camera)

        for i in range(4):
            camera_settings_frame.grid_rowconfigure(i, weight=1)

        connect_camera_button.grid(row=0, column=0, sticky="w")
        toggle_camera_checkbutton.grid(row=1, column=0, sticky="w")
        draw_markers_checkbutton.grid(row=2, column=0, sticky="w")
        draw_probe_tip_checkbutton.grid(row=3, column=0, sticky="w")
        draw_checkerboard_checkbutton.grid(row=4, column=0, sticky="w")

        return camera_settings_frame

    def toggle_camera(self):
        if self.camera.IsOpen():
            self.camera.Close()
            self.root.camera_object.updating = False
            self.camera_plot_frame.canvas.figure.axes[0].clear()
            self.camera_plot_frame.canvas.draw()
            self.log.log_event("Toggled Camera: OFF")
        else:
            self.camera.Open()
            self.root.camera_object.updating = True
            self.camera_thread = threading.Thread(target= lambda: update_camera(self.root))
            self.camera_thread.start()
            self.log.log_event("Toggled Camera: ON")
        

if __name__ == "__main__":
   
    from Python_Skripts.Function_Groups.hexapod import *
    from Python_Skripts.GUI import UserInterface

    root = tk.Tk()
    app = UserInterface(root, test_mode=True)



    path = r"C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\misc\Aruco-markers-4x4-50.png"
    root.camera_object.set_emulated_image(path)

    camera_panel = CameraPanel(root, root)
    camera_panel.panel.pack(side="top", fill="both", expand=True)
    

    root.mainloop()
    root.camera.Close()