import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Python_Skripts.GUI_Panels.Panel_Updates.update_slice_plot import update_slice_plot


def create_vertical_slice_plot_frame(parent, root):
    vertical_slice_plot_frame = tk.LabelFrame(parent, name="vertical_slice_plot_frame")
    vertical_slice_plot_frame.grid(row=2, column=0, rowspan=1, columnspan=1, sticky="nsew", padx=5, pady=5)
    
    plot_frame = tk.Frame(vertical_slice_plot_frame, name="plot_frame")
    # Create a canvas for the slice plot
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
    ax.set_xlabel('Y')
    ax.set_ylabel('Z')
    ax.set_title('Heatmap of Laser Beam')
    ax.invert_yaxis()  # invert y axis

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side = "top", fill= "none", expand=False)
    vertical_slice_plot_frame.canvas = canvas
    

    helper_frame = tk.Frame(vertical_slice_plot_frame, name="helper_frame")

    seperator = ttk.Separator(helper_frame, orient="horizontal")

    # Create a checkbox for the slice plot
    root.interpolation_var = tk.IntVar()
    interpolation_checkbox = tk.Checkbutton(helper_frame, text="Interpolation", name="interpolation_checkbox", variable=root.interpolation_var)
    
    root.vertical_slice_index_var = tk.IntVar(value = 1)
    vertical_slice_slider = tk.Scale(helper_frame, from_=1, to=2, orient="horizontal", name="vertical_slice_slider", variable=root.vertical_slice_index_var, resolution=1)
    slice_slider_label = ttk.Label(helper_frame, text=" Vertical Slice Index:", name="slice_slider_label")

    interpolation_checkbox.config(command=lambda: update_slice_plot(root))     
    vertical_slice_slider.config(command=lambda value: update_slice_plot(root)) # value to catch slider event


    for i in range(4):
        helper_frame.grid_rowconfigure(i, weight=1)
    
    helper_frame.grid_rowconfigure(1, weight=0) #weight for correct sizing of the slider
    

    seperator.grid(row=0, column=0, rowspan = 1, columnspan=2, sticky="nsew", pady=5)
    slice_slider_label.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)
    interpolation_checkbox.grid(row=1, column=1, columnspan=1, sticky="w", padx=5)
    vertical_slice_slider.grid(row=2, column=0, rowspan = 1, columnspan=2, sticky="nsew", padx=5)
    


    vertical_slice_plot_frame.grid_rowconfigure(0, weight=0)
    vertical_slice_plot_frame.grid_rowconfigure(1, weight=1)


    plot_frame.grid(row = 0, column = 0, rowspan = 1, columnspan = 1, sticky="nsew", padx=5, pady=5)
    helper_frame.grid(row = 1, column = 0, rowspan = 1, columnspan = 1, sticky="nsew", pady=5)


    return vertical_slice_plot_frame

def create_horizontal_slice_plot_frame(parent, root):
     
        horizontal_slice_plot_frame = tk.Frame(parent, name="horizontal_slice_plot_frame")

        # Create a canvas for the horizonatl slice plot
        plot_frame = tk.LabelFrame(horizontal_slice_plot_frame, name="plot_frame")
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
        #ax.set_aspect('equal')
        ax.set_xlabel('X')
        ax.set_ylabel('Z')
        ax.set_title('Horizontal Slice')
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side = "top", fill= "both", expand=True)  
        horizontal_slice_plot_frame.canvas = canvas


        # helper frame for the slider 
        helper_frame = tk.Frame(horizontal_slice_plot_frame, name="helper_frame")

        seperator = ttk.Separator(helper_frame, orient="horizontal")

        root.horizontal_slice_index_var = tk.IntVar(value = 1)
        horizontal_slice_slider_label = ttk.Label(helper_frame, text="Horizontal Slice Index:", name="horizontal_slice_slider_label")
        horizontal_slice_slider = tk.Scale(helper_frame, from_=1, to=2, orient="horizontal", name="horizontal_slice_slider", variable=root.horizontal_slice_index_var, resolution=1)
        horizontal_slice_slider.config(command=lambda value: update_slice_plot(root))


        for i in range(3):
            helper_frame.grid_rowconfigure(i, weight=1)

        #helper_frame.grid_rowconfigure(1, weight=10) #weight for correct sizing of the slider

        seperator.grid(row=0, column=0, rowspan = 1, columnspan=2, sticky="nsew",pady=5)
        horizontal_slice_slider_label.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)       
        horizontal_slice_slider.grid(row=2, column=0, rowspan = 1, columnspan=2, sticky="nsew", padx=5)
   
        
        # now actual grid
        for i in range(2):
            horizontal_slice_plot_frame.grid_rowconfigure(i, weight=1)

        plot_frame.grid(row = 0, column = 0, rowspan = 1, columnspan = 2, sticky="nsew", padx=5, pady=5)
        helper_frame.grid(row = 1, column = 0, rowspan = 1, columnspan = 2, sticky="nsew")
        
        return horizontal_slice_plot_frame