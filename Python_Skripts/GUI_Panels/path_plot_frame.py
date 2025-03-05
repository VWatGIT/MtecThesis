import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PathPlotFrame:
    def __init__(self, parent, root):
        self.frame = tk.Frame(parent, name="path_plot_frame")
        
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill= "both", expand=True)
        self.frame.canvas = canvas
        
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Path')
        ax.grid(True)