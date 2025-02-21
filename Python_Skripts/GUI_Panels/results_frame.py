import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from GUI_Panels.Panel_Updates.update_slice_plot import update_slice_plot
from GUI_Panels.sensor_info_frame import SensorInfoFrame 

class ResultsFrame:
    def __init__(self, parent, root):
        
        self.root = root
        self.frame = tk.LabelFrame(parent, text="Results", name="results_frame")

        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_rowconfigure(i, weight=1)
        
        sensor_info_frame = SensorInfoFrame(self.frame, root).frame
        slice_plot_frame = self.create_slice_plot_frame(self.frame)
        beam_plot_frame = self.create_beam_plot_frame(self.frame)
        


        beam_plot_frame.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)
        slice_plot_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=10, pady=10)
        sensor_info_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)

        self.frame.grid_rowconfigure(1, weight=7)



    def create_slice_plot_frame(self, parent):
        slice_plot_frame = tk.LabelFrame(parent, text="Slice", name="slice_plot_frame")
        for i in range(7):
            slice_plot_frame.grid_rowconfigure(i, weight=1)
        for i in range(1): 
            slice_plot_frame.grid_columnconfigure(i, weight=1)
        
        vertical_plot_frame = tk.LabelFrame(slice_plot_frame, name="vertical_plot_frame")
        vertical_plot_frame.grid(row=2, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=5)
        slice_plot_frame.grid_rowconfigure(2, weight=100) #weight for correct sizing of the slider
      
        # Create a canvas for the slice plot
        fig, ax = plt.subplots()
        ax.set_xlabel('Y')
        ax.set_ylabel('Z')
        ax.set_title('Heatmap of Laser Beam')
        ax.invert_yaxis()  # invert y axis

        canvas = FigureCanvasTkAgg(fig, master=vertical_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both")
        vertical_plot_frame.canvas = canvas
        
        # Create Labels for the Sliders
        slice_slider_label = ttk.Label(slice_plot_frame, text=" Vertical Slice Index:", name="slice_slider_label")
        slice_slider_label.grid(row=0, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)

        # Create a slider for the slice plot
        vertical_slice_slider = tk.Scale(slice_plot_frame, from_=1, to=2, orient="horizontal", name="vertical_slice_slider")
        vertical_slice_slider.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        vertical_slice_slider.set(1) # set default value
        vertical_slice_slider.config(resolution=1) # set slider resolution

        # Create the horizontal plot frame
        horizontal_plot_frame = tk.LabelFrame(slice_plot_frame, name="horizontal_plot_frame")
        horizontal_plot_frame.grid(row=4, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=5)

        # Create a canvas for the horizonatl slice plot
        fig, ax = plt.subplots()
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_title('Horizontal Slice')
        
        canvas = FigureCanvasTkAgg(fig, master=horizontal_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both")  
        horizontal_plot_frame.canvas = canvas



        # Create a Slider for horizontal slice plot
        horizontal_slice_slider_label = ttk.Label(slice_plot_frame, text="Horizontal Slice Index:", name="horizontal_slice_slider_label")
        horizontal_slice_slider_label.grid(row=5, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)

        horizontal_slice_slider = tk.Scale(slice_plot_frame, from_=1, to=2, orient="horizontal", name="horizontal_slice_slider")
        horizontal_slice_slider.grid(row=6, column=0, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        horizontal_slice_slider.set(1) # set default value
        horizontal_slice_slider.config(resolution=1) # set slider resolution

        slice_plot_frame.grid_rowconfigure(4, weight=100) #weight for correct sizing of the slider

        # Create a checkbox for the slice plot
        interpolation_var = tk.IntVar()
        interpolation_checkbox = tk.Checkbutton(slice_plot_frame, text="Interpolation", name="interpolation_checkbox", variable=interpolation_var)
        interpolation_checkbox.grid(row=3, column=0, columnspan=1, sticky="w", padx=5, pady=5)
        interpolation_checkbox.value = interpolation_var

        vertical_slice_slider.config(command=lambda: update_slice_plot(self.root))
        horizontal_slice_slider.config(command=lambda: update_slice_plot(self.root))
        interpolation_checkbox.config(command=lambda: update_slice_plot(self.root)) 

        return slice_plot_frame

    def create_beam_plot_frame(self, parent):
        
        beam_plot_frame = tk.LabelFrame(parent, text="Beam Plot", name="beam_plot_frame")

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.set_title('Beam Plot')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        canvas = FigureCanvasTkAgg(fig, master=beam_plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        beam_plot_frame.canvas = canvas

        return beam_plot_frame
