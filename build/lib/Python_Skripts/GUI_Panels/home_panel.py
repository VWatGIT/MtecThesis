import tkinter as tk
from tkinter import ttk

from Python_Skripts.GUI_Panels.Panel_Updates.panel_visibility import *

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
        
        #sep0 = ttk.Separator(self.frame, orient="horizontal")
        sep1 = ttk.Separator(self.frame, orient="horizontal")
        sep2 = ttk.Separator(self.frame, orient="horizontal")
        sep3 = ttk.Separator(self.frame, orient="horizontal")
        sep4 = ttk.Separator(self.frame, orient="horizontal")


        #sep0.pack(side="top", fill="x")
        new_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)     
        sep1.pack(side="top", fill="x")
        load_measurement_button.pack(side="top", padx=button_padx, pady=button_pady)
        sep2.pack(side="top", fill="x")
        camera_button.pack(side="top", padx=button_padx, pady=button_pady)
        sep3.pack(side="top", fill="x")
        help_button.pack(side="top", padx=button_padx, pady=button_pady)
        sep4.pack(side="top", fill="x")
