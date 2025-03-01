import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Python_Skripts.GUI_Panels.slice_plot_frames import create_vertical_slice_plot_frame, create_horizontal_slice_plot_frame
from Python_Skripts.GUI_Panels.sensor_info_frame import SensorInfoFrame 

class ResultsFrame:
    def __init__(self, parent, root):
        
        self.root = root
        self.frame = tk.LabelFrame(parent, name="results_frame")

        
        sensor_info_frame = SensorInfoFrame(self.frame, root).frame
        vertical_slice_plot_frame = create_vertical_slice_plot_frame(self.frame, root)
        horizontal_slice_plot_frame = create_horizontal_slice_plot_frame(self.frame, root)
        beam_plot_frame = self.create_beam_plot_frame(self.frame)
        

 

        self.frame.columnconfigure(0, weight=0)
        self.frame.columnconfigure(1, weight=10)
        self.frame.columnconfigure(2, weight=100)

        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=2)

        
        

        beam_plot_frame.grid(row=0, column=0,rowspan=2, columnspan=1, sticky="nsew", padx=5, pady=5)
        vertical_slice_plot_frame.grid(row=0, column=1, columnspan=1, sticky="nsew", padx=5, pady=5)
        sensor_info_frame.grid(row=0, column=2, columnspan=1, sticky="nsew", padx=5, pady=5)
        horizontal_slice_plot_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", padx=5, pady=5)





    def create_beam_plot_frame(self, parent):
        
        beam_plot_frame = tk.LabelFrame(parent, name="beam_plot_frame")

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
        ax.set_aspect('equal')
        ax.set_title('Measured Beam')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        canvas = FigureCanvasTkAgg(fig, master=beam_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        beam_plot_frame.canvas = canvas

        return beam_plot_frame
