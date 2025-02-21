import tkinter as tk
from tkinter import ttk

from GUI_Panels.event_log_panel import EventLogPanel
from GUI_Panels.tab_group import TabGroup
from GUI_Panels.camera_panel import CameraPanel
from GUI_Panels.help_panel import HelpPanel

class PanedWindow:
    def __init__(self, parent, root):
        self.root = root
        
        self.paned_window = ttk.PanedWindow(parent, orient="vertical")
        

        self.root.paned_window = self.paned_window
        
        self.helper_frame = tk.Frame(self.paned_window)

        self.event_log = EventLogPanel(self.paned_window, root)
        self.event_log_panel = self.event_log.panel
        self.event_log_panel.pack(side="right", fill="x", padx=10, pady=10)


        self.root.log = self.event_log # for logging call root.log.log_event("message")

        self.paned_window.add(self.helper_frame)
        self.paned_window.add(self.event_log_panel)

        self.tab_group_object = TabGroup(self.helper_frame, root)
        self.root.tab_group_object = self.tab_group_object
        self.tab_group = self.tab_group_object.tab_group

        self.camera_panel_object = CameraPanel(self.helper_frame, root)
        self.camera_panel = self.camera_panel_object.panel

        self.help_panel_object = HelpPanel(self.helper_frame, root)
        self.help_panel = self.help_panel_object.panel

        # Set Sashposition of the paned window
        self.paned_window.after(200, lambda: self.paned_window.sashpos(0, 840)) # after for short delay (bugfix)
        