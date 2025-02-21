import tkinter as tk
from tkinter import ttk

from GUI_Panels.Panel_Updates.panel_visibility import *

class HomePanel:
    def __init__(self, parent, root):
        self.frame = tk.Frame(parent)

        self.root = root
        self.root.home_panel = self.frame

        button_width = 20  
        button_height = 3  
        button_padx = 0   
        button_pady = 40  

        new_measurement_button = tk.Button(self.frame, text="New Measurement", command= lambda: show_new_measurement_panel(root), width=button_width, height=button_height)
        load_measurement_button = tk.Button(self.frame, text="Load Measurement", command= lambda: show_load_measurement_panel(root), width=button_width, height=button_height)
        camera_button = tk.Button(self.frame, text="Camera", command= lambda: show_camera_panel(root), width=button_width, height=button_height)
        help_button = tk.Button(self.frame, text="Help", command= lambda: show_help_panel(root), width=button_width, height=button_height)
        
        new_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)        
        load_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)
        camera_button.pack(side="top", padx=button_padx, pady=button_pady)
        help_button.pack(side="top", padx=button_padx, pady=button_pady)
