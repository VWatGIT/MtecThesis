import tkinter as tk

from GUI_Panels.menu import create_menu
from GUI_Panels.left_panel import LeftPanel
from GUI_Panels.paned_window import PanedWindow

from GUI_Panels.Panel_Updates.panel_visibility import *

def create_top_panel(root):
    top_panel = tk.Frame(root, name="top_panel")
    top_panel.place(relx=0, rely=0, anchor="nw", relheight=1, relwidth=1)

    # ORDER OF CREATION MATTERS
    paned_window = PanedWindow(root, root).paned_window # 1st
    left_panel = LeftPanel(root, root).frame # 2nd
    menu = create_menu(root) # 3rd

    paned_window.pack(side="right", expand=True, fill="both")
    left_panel.pack(side="left", fill="both")

    show_home_panel(root)
    show_camera_panel(root)
    return top_panel