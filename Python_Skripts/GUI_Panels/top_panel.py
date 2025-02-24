import tkinter as tk
from tkinter import ttk

from Python_Skripts.GUI_Panels.menu import create_menu
from Python_Skripts.GUI_Panels.left_panel import LeftPanel
from Python_Skripts.GUI_Panels.paned_window import PanedWindow

from Python_Skripts.GUI_Panels.Panel_Updates.panel_visibility import *

def create_top_panel(root):
    top_panel = tk.Frame(root, name="top_panel")
    top_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

    # ORDER OF CREATION MATTERS
    paned_window = PanedWindow(top_panel, root).paned_window # 1st
    left_panel = LeftPanel(top_panel, root).frame # 2nd
    menu = create_menu(root) # 3rd
    seperator = ttk.Separator(top_panel, orient="vertical") # 4th
    seperator2 = ttk.Separator(top_panel, orient="horizontal") # 5th
    
    seperator2.pack(side="top", fill="x")
    left_panel.pack(side="left", fill="both")
    seperator.pack(side="left", fill="y")
    paned_window.pack(side="right", expand=True, fill="both")


    show_home_panel(root)
    show_camera_panel(root)
    return top_panel