import tkinter as tk

from GUI_Panels.Panel_Updates.panel_visibility import *

def create_menu(root):
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    menubar.add_command(label="Home", command=lambda:show_home_panel(root))
    menubar.add_command(label="New", command=lambda:show_new_measurement_panel(root))
    menubar.add_command(label="Load", command=lambda:show_load_measurement_panel(root))
    menubar.add_command(label="Camera", command=lambda:show_camera_panel(root))
    menubar.add_command(label="Help", command=lambda:show_help_panel(root))