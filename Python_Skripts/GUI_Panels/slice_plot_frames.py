import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from Python_Skripts.GUI_Panels.Panel_Updates.update_slice_plot import update_slice_plot


def create_vertical_slice_plot_frame(parent, root):
    vertical_slice_plot_frame = tk.LabelFrame(parent, name="vertical_slice_plot_frame")
    
    plot_frame = tk.Frame(vertical_slice_plot_frame, name="plot_frame")
    # Create a canvas for the slice plot
    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
    fig.tight_layout()
    #ax.invert_yaxis()  # invert y axis
    ax.set_aspect('equal')
    

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill= "both", expand=True)  #side = "top",
    vertical_slice_plot_frame.canvas = canvas
    

    helper_frame = tk.Frame(vertical_slice_plot_frame, name="helper_frame")

    seperator = ttk.Separator(helper_frame, orient="horizontal")

    root.vertical_slice_index_var = tk.IntVar(value = 1)
    vertical_slice_slider = tk.Scale(helper_frame, from_=1, to=2, orient="horizontal", name="vertical_slice_slider", variable=root.vertical_slice_index_var, resolution=1)
    slice_slider_label = ttk.Label(helper_frame, text=" Vertical Slice Index:", name="slice_slider_label")

    vertical_slice_slider.config(command=lambda value: update_slice_plot(root)) # value to catch slider event


    for i in range(2):
        helper_frame.grid_rowconfigure(i, weight=1)
    
    for i in range(2):
        helper_frame.grid_columnconfigure(i, weight=0)

    helper_frame.grid_columnconfigure(1, weight=10) #weight for correct sizing of the slider

    seperator.grid(row=0, column=0, rowspan = 1, columnspan=2, sticky="nsew", )
    slice_slider_label.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)
    vertical_slice_slider.grid(row=1, column=1, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
    


    vertical_slice_plot_frame.grid_rowconfigure(0, weight=2, minsize=370)
    vertical_slice_plot_frame.grid_rowconfigure(1, weight=1, minsize=70)

    vertical_slice_plot_frame.grid_columnconfigure(0, weight=1, minsize=400)

    plot_frame.grid(row = 0, column = 0, rowspan = 1, columnspan = 1, sticky="nsew")
    helper_frame.grid(row = 1, column = 0, rowspan = 1, columnspan = 1, sticky="nsew")


    return vertical_slice_plot_frame

def create_horizontal_slice_plot_frame(parent, root):
     
        horizontal_slice_plot_frame = tk.LabelFrame(parent, name="horizontal_slice_plot_frame")

        # Create a canvas for the horizonatl slice plot
        plot_frame = tk.Frame(horizontal_slice_plot_frame, name="plot_frame")
        fig, ax = plt.subplots()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0) # expand to fill the whole canvas
        fig.tight_layout()
        #ax.set_aspect('equal')
        ax.set_aspect('auto')
        ax.invert_yaxis()  # invert y axis
        
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)  #side = "top", 
        horizontal_slice_plot_frame.canvas = canvas


        # helper frame for the slider 
        helper_frame = tk.Frame(horizontal_slice_plot_frame, name="helper_frame")

        seperator = ttk.Separator(helper_frame, orient="horizontal")

            
        root.interpolation_var = tk.IntVar()
        interpolation_checkbox = tk.Checkbutton(helper_frame, text="Interpolation", name="interpolation_checkbox", variable=root.interpolation_var)
        interpolation_checkbox.config(command=lambda: update_slice_plot(root))     
        


        root.horizontal_slice_index_var = tk.IntVar(value = 1)
        horizontal_slice_slider_label = ttk.Label(helper_frame, text="Horizontal Slice Index:", name="horizontal_slice_slider_label")
        horizontal_slice_slider = tk.Scale(helper_frame, from_=1, to=2, orient="horizontal", name="horizontal_slice_slider", variable=root.horizontal_slice_index_var, resolution=1)
        horizontal_slice_slider.config(command=lambda value: update_slice_plot(root))


        for i in range(3):
            helper_frame.grid_rowconfigure(i, weight=1)

        for i in range(3): 
            helper_frame.grid_columnconfigure(i, weight=0)

        helper_frame.grid_columnconfigure(1, weight=10) #weight for correct sizing of the slider
       
        seperator.grid(row=0, column=0, rowspan = 1, columnspan=3, sticky="nsew")
        horizontal_slice_slider_label.grid(row=1, column=0, rowspan = 1, columnspan=1, sticky="w", padx=5)       
        horizontal_slice_slider.grid(row=1, column=1, rowspan = 1, columnspan=1, sticky="nsew", padx=5)
        #interpolation_checkbox.place(relx=1, rely=1)
        interpolation_checkbox.grid(row=1, column=3, columnspan=1, sticky="w", padx=5)



        horizontal_slice_plot_frame.grid_rowconfigure(0, weight=2, minsize=140)
        horizontal_slice_plot_frame.grid_rowconfigure(1, weight=1, minsize=70)

        horizontal_slice_plot_frame.grid_columnconfigure(0, weight=1, minsize=700)
        plot_frame.grid(row = 0, column = 0, rowspan = 1, columnspan = 1, sticky="nsew")
        helper_frame.grid(row = 1, column = 0, rowspan = 1, columnspan = 1, sticky="nsew")
        
        return horizontal_slice_plot_frame