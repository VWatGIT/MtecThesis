import tkinter as tk
from tkinter import ttk

from Python_Skripts.GUI_Panels.sensor_info_frame import SensorInfoFrame
from Python_Skripts.GUI_Panels.path_plot_frame import PathPlotFrame


class SensorPathFrame:
    def __init__(self, parent, root):
        self.frame = ttk.Frame(parent, name="sensor_path_frame")

        #self.sensor_info_frame = SensorInfoFrame(self.frame, root).frame
        self.path_plot_frame = PathPlotFrame(self.frame, root).frame

        #self.sensor_info_frame.pack(side="left", fill="both", expand=True)
        self.path_plot_frame.pack(side="right", fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SensorPathFrame(root, root)
    app.frame.pack(fill="both", expand=True)
    root.mainloop()

