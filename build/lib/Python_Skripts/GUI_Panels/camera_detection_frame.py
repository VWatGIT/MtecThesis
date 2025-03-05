import tkinter as tk

from Python_Skripts.Function_Groups.camera import *
from Python_Skripts.Function_Groups.probe_tip_detection import *
from Python_Skripts.Function_Groups.marker_detection import detect_markers

class ProbeDetectionFrame:
    def __init__(self, parent, root):
        self.root = root
        self.camera_object = root.camera_object
        self.camera = root.camera_object.camera
        self.probe = root.probe
        self.canvas = root.camera_plot_frame.canvas

        self.frame = tk.LabelFrame(parent, text="Probe-Tip detection", name="probe_detection_frame")

        for i in range(5):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        # Define labels and entries
        self.crop_top_left_label = tk.Label(self.frame, text="Top Left Corner: [x,y]", name="crop_top_left_label")
        self.crop_top_left_entry = tk.Entry(self.frame, name="crop_top_left_entry")
        self.crop_top_left_entry.insert(0, "0,0")

        self.crop_bottom_right_label = tk.Label(self.frame, text="Bottom Right Corner: [x,y]", name="crop_bottom_right_label")
        self.crop_bottom_right_entry = tk.Entry(self.frame, name="crop_bottom_right_entry")
        self.crop_bottom_right_entry.insert(0, "1920,1080")

        self.threshold_slider_label = tk.Label(self.frame, text="Threshold Value", name="threshold_slider_label")
        self.threshold_slider = tk.Scale(self.frame, from_=0, to=255, orient="horizontal", name="threshold_slider")
        self.threshold_slider.config(command=self.take_probe_image)

        self.take_probe_image_button = tk.Button(self.frame, text="Take Image", command=self.take_probe_image)

        self.save_probe_position_button = tk.Button(self.frame, text="Save Position", command=self.save_probe_position, state="disabled")

        # Place labels and entries using grid
        self.crop_top_left_label.grid(row=0, column=0, pady=5, sticky="w")
        self.crop_top_left_entry.grid(row=0, column=1, pady=5, sticky="w")

        self.crop_bottom_right_label.grid(row=1, column=0, pady=5, sticky="w")
        self.crop_bottom_right_entry.grid(row=1, column=1, pady=5, sticky="w")

        self.threshold_slider_label.grid(row=2, column=0, rowspan=2, pady=5, sticky="w")
        self.threshold_slider.grid(row=2, column=1, rowspan=2, pady=5, sticky="w")

        self.take_probe_image_button.grid(row=4, column=0, columnspan=2, rowspan=2, pady=5, sticky="w")

        self.frame.grid_rowconfigure(3, weight=3)  # weight row for gap
        self.save_probe_position_button.grid(row=6, column=1, pady=5, sticky="w")


    def take_probe_image(self, event=None):
        # updates the canvas with the detected image
        top_left = tuple(map(int, self.crop_top_left_entry.get().split(',')))
        bottom_right = tuple(map(int, self.crop_bottom_right_entry.get().split(',')))

        image = self.camera_object.capture_image()
        image = crop_image(image, top_left, bottom_right)

        # Detect the needle tip
        threshold = self.threshold_slider.get()
        result_image, detected_probe_position_cropped, pixel_size = detect_needle_tip(image, threshold)

        # translate the cropped coordinates to the original image
        if detected_probe_position_cropped is not None:
            # calculate position in original image
            detected_position = crop_coordinate_transform(image, detected_probe_position_cropped, top_left)
            
            self.root.probe.set_probe_tip_position(detected_position)

            self.root.log.log_event(f"Probe-Tip detected at {self.root.probe.probe_tip_position_in_camera_image}")
            self.save_probe_position_button.config(state="normal")  
        else:
            self.root.probe_tip_position_in_camera_image = None
            self.save_probe_position_button.config(state="disabled")

            self.root.log.log_event("Probe-Tip not detected")

        # Show the result
        canvas = self.root.camera_plot_frame.canvas
        axes = self.root.camera_plot_frame.canvas.figure.axes[0]
        axes.clear()
        axes.imshow(result_image, theta = 0.5)  # Show image with detected tip drawn
        canvas.draw()
        axes.axis('off')

        self.root.log.log_event("Took Probe Image")

    def save_probe_position(self):
        self.probe_detected = True
        self.probe_detetection_checkbox.select()

        self.new_measurement_panel.nametowidget("checkbox_panel").nametowidget("probe_detected").select()
        self.probe.translate_probe_tip(self.detected_probe_position, self.mtx, self.dist)
        self.root.log.log_event("Saved Probe Position")

class MarkerDetectionFrame:
    def __init__(self, parent, root):
        self.camera = root.camera  # TODO check where i create this
        self.sensor = root.sensor
        self.probe = root.probe
        self.canvas = root.camera_plot_frame.canvas

        self.frame = tk.LabelFrame(parent, text="Marker detection", name="marker_detection_frame")

        for i in range(5):
            self.frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)

        # Define labels and entries
        self.probe_marker_id_label = tk.Label(self.frame, text="Probe Marker ID:", name="probe_marker_id_label")
        self.sensor_marker_id_label = tk.Label(self.frame, text="Sensor Marker ID:", name="sensor_marker_id_label")

        self.probe_marker_id_entry = tk.Entry(self.frame, name="probe_marker_id_entry")
        self.sensor_marker_id_entry = tk.Entry(self.frame, name="sensor_marker_id_entry")

        self.probe_marker_id_entry.insert(0, str(self.probe.marker_id))
        self.sensor_marker_id_entry.insert(0, str(self.sensor.marker_id))

        # Place labels and entries using grid
        self.probe_marker_id_label.grid(row=0, column=0, pady=5, sticky="w")
        self.sensor_marker_id_label.grid(row=1, column=0, pady=5, sticky="w")
        self.probe_marker_id_entry.grid(row=0, column=1, pady=5, sticky="w")
        self.sensor_marker_id_entry.grid(row=1, column=1, pady=5, sticky="w")



