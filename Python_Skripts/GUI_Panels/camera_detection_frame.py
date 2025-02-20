import tkinter as tk

from Function_Groups.camera import *
from Function_Groups.probe_tip_detection import *

from Function_Groups.marker_detection import detect_markers

class ProbeDetectionFrame:
    def __init__(self, parent, root):
        
        self.camera = root.camera
        self.probe = root.probe
        self.canvas = root.camera_plot_frame.canvas
         

        self.probe_detected = False
        self.detected_probe_position = None

        self.frame = tk.Frame(parent, name="probe_detection_frame")

        
        for i in range(5):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)


        self.crop_top_left_label = tk.Label(self.frame, text="Top Left Corner: [x,y]", name="crop_top_left_label")
        self.crop_top_left_label.grid(row=0, column=0, pady=5)
        self.crop_top_left_entry = tk.Entry(self.frame, name="crop_top_left_entry")
        self.crop_top_left_entry.grid(row=0, column=1, pady=5)
        self.crop_top_left_entry.insert(0, "0,0")

        self.crop_bottom_right_label = tk.Label(self.frame, text="Bottom Right Corner: [x,y]", name="crop_bottom_right_label")
        self.crop_bottom_right_label.grid(row=1, column=0, pady=5)
        self.crop_bottom_right_entry = tk.Entry(self.frame, name="crop_bottom_right_entry")
        self.crop_bottom_right_entry.grid(row=1, column=1, pady=5)
        self.crop_bottom_right_entry.insert(0, "1920,1080")

        self.threshold_slider_label = tk.Label(self.frame, text="Threshold Value", name="threshold_slider_label") 
        self.threshold_slider_label.grid(row=2, column=0, rowspan=2, pady=5)
        self.threshold_slider = tk.Scale(self.frame, from_=0, to=255, orient="horizontal", name="threshold_slider")
        self.threshold_slider.grid(row=2, column=1, rowspan=2, pady=5)
        self.threshold_slider.config(command=self.take_probe_image)


        self.take_probe_image_button = tk.Button(self.frame, text="Take Image", command=self.take_probe_image) 
        self.take_probe_image_button.grid(row=4, column=0, columnspan=2,rowspan = 2,pady=5)

        self.frame.grid_rowconfigure(3, weight=3) #weight row for gap
        
        self.save_probe_position_button = tk.Button(self.frame, text="Save Position", command=self.save_probe_position, state="disabled") # TODO implement detect_probe
        self.save_probe_position_button.grid(row=6, column=1, pady=5)

        self.probe_detetection_checkbox = tk.Checkbutton(self.frame, text="Probe Detected", name="probe_detected", state="disabled")
        self.probe_detetection_checkbox.grid(row=6, column=0, pady=5)


   

    def take_probe_image(self):
        # updates the canvas with the detected image
        # TODO access the entries in a different way, not by .self
        top_left = tuple(map(int, self.crop_top_left_entry.get().split(',')))
        bottom_right = tuple(map(int, self.crop_bottom_right_entry.get().split(',')))

        self.camera.Open()
        image = capture_image(self.camera)
        self.camera.Close()

        image = crop_image(image, top_left, bottom_right)

        # Detect the needle tip
        threshold = self.threshold_slider.get()
        result_image, detected_probe_position_cropped, pixel_size = detect_needle_tip(image, threshold) # TODO add probe rotation detection

        # translate the cropped coordinates to the original image
        
        if detected_probe_position_cropped is not None:
            self.detected_probe_position = crop_coordinate_transform(image, detected_probe_position_cropped, top_left)
            self.log_event(f"Probe-Tip detected at {self.detected_probe_position}")
            self.save_probe_position_button.config(state="normal")
            self.probe_detetection_checkbox.config(state="normal")
        else:
            self.detected_probe_position = None
            self.save_probe_position_button.config(state="disabled")
            self.probe_detetection_checkbox.config(state="disabled")
            self.log_event("Probe-Tip not detected")


        # Show the result
        canvas = self.probe_plot_frame.canvas
        axes = self.probe_plot_frame.canvas.figure.axes[0]
        axes.clear()
        axes.imshow(result_image) # Show image with detected tip drawn
        canvas.draw()
        axes.axis('off')

        self.log_event("Took Probe Image")

    def save_probe_position(self):
        # TODO maybe merge this with take probe image

        self.probe_detected = True
        self.probe_detetection_checkbox.select()

        
        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("probe_detected").select()
        self.probe.translate_probe_tip(self.detected_probe_position, self.mtx, self.dist)
        self.log_event("Saved Probe Position")


class MarkerDetectionFrame:
    def __init__(self, parent, root):
        self.camera = root.camera # TODO check where i create this
        self.sensor = root.sensor
        self.probe = root.probe
        self.canvas = root.camera_plot_frame.canvas

        self.frame = tk.Frame(parent, name="marker_detection_frame")
        
    def scan_markers(self, image):
        # TODO where do i get mtx and dist from
        image, rvecs, tvecs = detect_markers(image, self.camera.mtx, self.camera.dist)

        self.sensor.marker_rvecs = rvecs[self.sensor.marker_id]
        self.sensor.marker_tvecs = tvecs[self.sensor.marker_id]

        self.probe.marker_rvecs = rvecs[self.probe.marker_id]
        self.probe.marker_tvecs = tvecs[self.probe.marker_id]

        self.update_marker_plot(image)

    def update_marker_plot(self, image):
        # TODO implement marker detection plot
        pass
    

