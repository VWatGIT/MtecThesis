import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_camera_plot_frame(self, parent):
    camera_plot_frame = tk.LabelFrame(parent, text="Camera Image", name="camera_plot_frame")
    fig, ax = plt.subplots()
    canvas = FigureCanvasTkAgg(fig, master=camera_plot_frame)
    canvas.get_tk_widget().place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)
    camera_plot_frame.canvas = canvas
    ax.axis('off')
    return camera_plot_frame

