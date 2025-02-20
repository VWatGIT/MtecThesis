import tkinter as tk
from tkinter import ttk

from sensor_info_frame import SensorInfoFrame
from path_plot_frame import PathPlotFrame


class SensorPathFrame:
    def __init__(self, parent, root):
        self.frame = ttk.Frame(parent, name="sensor_path_frame")

        self.sensor_info_frame = SensorInfoFrame(self.frame, root).frame
        self.path_plot_frame = PathPlotFrame(self.frame, root).frame

        self.sensor_info_frame.pack(side="left", fill="both", expand=True)
        self.path_plot_frame.pack(side="right", fill="both", expand=True)


