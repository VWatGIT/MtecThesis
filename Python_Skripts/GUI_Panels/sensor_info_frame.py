import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Python_Skripts.GUI_Panels.Panel_Updates.update_tab import update_tab

class SensorInfoFrame:
    def __init__(self, parent, root):
        # Create the main sensor_info_frame LabelFrame
        self.frame = tk.LabelFrame(parent, text="Measurement N/A" , name="sensor_info_frame")#, width=500, height=500)
    
        # Configure the grid layout within the self.frame LabelFrame
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            self.frame.grid_rowconfigure(i, weight=1)

        sensor_readings_frame = self.create_sensor_readings_frame(self.frame)
        sensor_plot_frame = self.create_sensor_plot_frame(self.frame)
                                                                                            
        measurement_slider = tk.Scale(self.frame, from_=1, to=100, orient="horizontal", name="measurement_slider", variable=root.measurement_id_var)
        measurement_slider.set(1)
        measurement_slider.config(resolution=1, state="normal", command = lambda: update_tab(root))

     
        self.measurement_slider = measurement_slider

        self.frame.grid_rowconfigure(1, weight=100)
        self.frame.grid_columnconfigure(1, weight=100)


        measurement_slider.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10)
        sensor_readings_frame.grid(row=1, column=1, columnspan=1, sticky="nsew", padx=10, pady=10)
        sensor_plot_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", padx=10, pady=10)     

    def create_sensor_readings_frame(self, parent):    

        # Create a LabelFrame for X and Y positions
        sensor_readings_frame = tk.LabelFrame(parent, text="Sensor Readings", name="sensor_readings_frame")

        for i in range(5):
            sensor_readings_frame.grid_rowconfigure(i, weight=1)

        # Add labels to display X and Y positions within the sensor_readings_frame
        xpos_label = tk.Label(sensor_readings_frame, text="X Position: N/A", name="xpos_label")
        xpos_label.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        ypos_label = tk.Label(sensor_readings_frame, text="Y Position: N/A", name="ypos_label")
        ypos_label.grid(row=1, column=0, sticky="nw", padx=10, pady=5)

        sum_label = tk.Label(sensor_readings_frame, text="Sum: N/A", name="sum_label")
        sum_label.grid(row=2, column=0, columnspan=2, sticky="nw", padx=10, pady=5)

        xdiff_label = tk.Label(sensor_readings_frame, text="X Diff: N/A", name="xdiff_label")
        xdiff_label.grid(row=3, column=0, sticky="nw", padx=10, pady=5)

        ydiff_label = tk.Label(sensor_readings_frame, text="Y Diff: N/A", name="ydiff_label")
        ydiff_label.grid(row=4, column=0, sticky="nw", padx=10, pady=5)

        return sensor_readings_frame

    def create_sensor_plot_frame(self, parent):
        # Create a plotframe for the sensor plot
        sensor_plot_frame = tk.LabelFrame(parent, text="Detected Laser Position", name="sensor_plot_frame")
        
        # display the sensor data in a plot
        fig, ax = plt.subplots()

        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_title('Sensor Output')
        ax.grid(True)
        ax.legend(['Signal Position'])

        ax.set_aspect('equal')
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)

        canvas = FigureCanvasTkAgg(fig, master=sensor_plot_frame) 
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)   
        sensor_plot_frame.canvas = canvas # store canvas in sensor_plot_frame

        return sensor_plot_frame

