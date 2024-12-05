import numpy as np
from pypylon import pylon
import cv2
import glob
import os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt


def detect_markers(image, mtx, dist):
    """
    Detect ArUco markers in the image and estimate their pose.

    Parameters:
    image (numpy.ndarray): The input image.
    mtx (numpy.ndarray): Camera matrix.
    dist (numpy.ndarray): Distortion coefficients.

    Returns:
    image (numpy.ndarray): The image with detected markers and axes drawn.
    rvecs (list): Rotation vectors of the detected markers.
    tvecs (list): Translation vectors of the detected markers.
    """
    # Load the predefined dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()

    # Detect the markers in the image
    corners, ids, rejectedImgPoints = cv2.aruco.detectMarkers(image, aruco_dict, parameters=parameters)

    if ids is not None:
        # Estimate pose of each marker
        rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(corners, 0.016, mtx, dist)  # 0.016 is the marker length in meters

        # Draw detected markers and their axes
        cv2.aruco.drawDetectedMarkers(image, corners, ids)
        
    else:
        rvecs = []
        tvecs = []
    
    return image, rvecs, tvecs


class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Marker Detection")
        self.root.geometry("800x600")

        self.detection_frame = tk.Frame(self.root, name="detection_frame")
        self.detection_frame.grid(row=0, column=0, sticky="nsew")

        for i in range(2):
            self.detection_frame.grid_columnconfigure(i, weight=1)

        self.create_marker_detection_input_frame(self.detection_frame)
        self.create_marker_detection_plot_frame(self.detection_frame)

        marker_detection_input_frame = self.detection_frame.nametowidget("marker_detection_input_frame")
        marker_detection_plot_frame = self.detection_frame.nametowidget("marker_detection_plot_frame")

        marker_detection_input_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        marker_detection_plot_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

    


    def create_marker_detection_input_frame(self, parent):
        marker_detection_input_frame = tk.Frame(parent, name="marker_detection_input_frame")

        for i in range(4):
            marker_detection_input_frame.grid_rowconfigure(i, weight=1)
        for i in range(2):
            marker_detection_input_frame.grid_columnconfigure(i, weight=1)

        sensor_marker_id_label = tk.Label(marker_detection_input_frame, text="Sensor Marker ID:")
        sensor_marker_id_label.grid(row=0, column=0, sticky="w", pady=5)
        sensor_marker_id_entry = tk.Entry(marker_detection_input_frame, name="sensor_marker_id_entry")
        sensor_marker_id_entry.grid(row=0, column=1, sticky="w", pady=5)
        sensor_marker_id_entry.insert(0, "0")

        sensor_marker_size_label = tk.Label(marker_detection_input_frame, text="Sensor Marker Size [mm]:")
        sensor_marker_size_label.grid(row=1, column=0, sticky="w", pady=5)
        sensor_marker_size_entry = tk.Entry(marker_detection_input_frame, name="sensor_marker_size_entry")
        sensor_marker_size_entry.grid(row=1, column=1, sticky="w", pady=5)
        sensor_marker_size_entry.insert(0, "16") # TODO change with actual size

        marker_detected_checkbox = tk.Checkbutton(marker_detection_input_frame, text="Marker Detected",name="marker_detected_checkbox", state="disabled")
        marker_detected_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)

        update_markers_button = tk.Button(marker_detection_input_frame, text="Update", command=detect_markers) # TODO pass image and calibrations stuff to detect markers
        update_markers_button.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        

    def create_marker_detection_plot_frame(self, parent):
        marker_detection_plot_frame = tk.Frame(parent, name="marker_detection_plot_frame")

        fig, ax = plt.subplots()
        canvas = FigureCanvasTkAgg(fig, master=marker_detection_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        marker_detection_plot_frame.canvas = canvas


if __name__ == "__main__":

    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()