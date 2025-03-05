import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_plot import update_beam_plot
from Python_Skripts.GUI_Panels.Panel_Updates.update_sensor_info_frame import update_sensor_info_frame

class SensorInfoFrame:
    def __init__(self, parent, root):
        tab = root.tab_group.nametowidget(root.tab_group.select())
        
        # Create the main sensor_info_frame LabelFrame
        self.frame = tk.LabelFrame(parent, text="Measurement N/A" , name="sensor_info_frame")#, width=500, height=500)
    
        # Configure the grid layout within the self.frame LabelFrame
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(4):
            self.frame.grid_rowconfigure(i, weight=1)

        sensor_readings_frame = self.create_sensor_readings_frame(self.frame)
        sensor_plot_frame = self.create_sensor_plot_frame(self.frame)

        root.measurement_slider_var = tk.IntVar(value=1) #  should not be attached to the root, but to tab is a fix for now
        measurement_slider = tk.Scale(self.frame, from_=1, orient="horizontal", name="measurement_slider", variable=root.measurement_slider_var)
        measurement_slider.set(1)
        measurement_slider.config(resolution=1, state="normal", command = lambda value: self.update_all(root)) # value to catch slider event
        self.measurement_slider = measurement_slider

        seperator = tk.ttk.Separator(self.frame, orient="horizontal")
        seperator_2 = tk.ttk.Separator(self.frame, orient="horizontal")

        self.frame.grid_rowconfigure(0, weight=1, minsize=45)
        self.frame.grid_rowconfigure(1, weight=0, minsize=5)
        self.frame.grid_rowconfigure(2, weight=1, minsize=125)
        self.frame.grid_rowconfigure(3, weight= 1, minsize=5)
        self.frame.grid_rowconfigure(4, weight= 1, minsize=70)


        self.frame.grid_columnconfigure(0, weight= 1, minsize=200)
        
        measurement_slider.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=5)
        seperator.grid(row=1, column=0, columnspan=1, sticky="nsew")


        sensor_plot_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")     
        seperator_2.grid(row=3, column=0, columnspan=1, sticky="nsew")
        sensor_readings_frame.grid(row=4, column=0, columnspan=1, sticky="nsew")

    def create_sensor_readings_frame(self, parent):    

        # Create a LabelFrame for X and Y positions
        sensor_readings_frame = tk.Frame(parent, name="sensor_readings_frame")

        for i in range(2):
            sensor_readings_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            sensor_readings_frame.grid_columnconfigure(i, weight=1)

        # Add labels to display X and Y positions within the sensor_readings_frame
        xpos_label = tk.Label(sensor_readings_frame, text="X Position: N/A", name="xpos_label")
        ypos_label = tk.Label(sensor_readings_frame, text="Y Position: N/A", name="ypos_label")
        sum_label = tk.Label(sensor_readings_frame, text="Sum: N/A", name="sum_label")
        xdiff_label = tk.Label(sensor_readings_frame, text="X Diff: N/A", name="xdiff_label")
        ydiff_label = tk.Label(sensor_readings_frame, text="Y Diff: N/A", name="ydiff_label")

        xpos_label.grid(row=0, column=0, sticky="w", pady=5)
        ypos_label.grid(row=1, column=0, sticky="w", pady=5)
        xdiff_label.grid(row=0, column=1, sticky="w", pady=5)
        ydiff_label.grid(row=1, column=1, sticky="w", pady=5)
        sum_label.grid(row=0, column=2, rowspan=2, sticky="w", pady=5)


        return sensor_readings_frame


    def create_sensor_plot_frame(self, parent):
        # Create a plotframe for the sensor plot
        sensor_plot_frame = tk.Frame(parent, name="sensor_plot_frame")
        
        # display the sensor data in a plot
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        fig.tight_layout()
        ax.grid(True)
        
        ax.set_aspect('equal')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

        canvas = FigureCanvasTkAgg(fig, master=sensor_plot_frame) 
        canvas.draw()
        canvas.get_tk_widget().pack(side = "top", fill= "both", expand=True)   
        sensor_plot_frame.canvas = canvas # store canvas in sensor_plot_frame

        return sensor_plot_frame

    def update_all(self, root):
        update_sensor_info_frame(root)
        update_beam_plot(root)