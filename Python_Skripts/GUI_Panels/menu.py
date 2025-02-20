import tkinter as tk

from Panel_Updates.panel_visibility import *

def create_menu(root):
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    menubar.add_command(label="Home", command=show_home_panel(root))
    menubar.add_command(label="New", command=show_new_measurement_panel(root))
    menubar.add_command(label="Load", command=show_load_measurement_panel(root))
    menubar.add_command(label="Camera", command=show_camera_panel(root))
    menubar.add_command(label="Help", command=show_help_panel(root))