import tkinter as tk
from tkinter import ttk

from .event_log_panel import EventLogPanel
from .tab_group import TabGroup
from .camera_panel import CameraPanel
from .help_panel import HelpPanel

class PanedWindow:
    def __init__(self, parent, root):
        self.paned_window = ttk.PanedWindow(parent, orient="vertical")
        self.paned_window.pack(expand=True, fill="both")
        
        self.helper_frame = tk.Frame(self.paned_window)

        self.event_log = EventLogPanel(self.paned_window)
        self.event_log_panel = self.event_log.panel

        self.paned_window.add(self.helper_frame)
        self.paned_window.add(self.event_log_panel)

        self.tab_group_object = TabGroup(self.helper_frame, self.new_data)
        self.tab_group = self.tab_group_object.tab_group

        self.camera_panel_object = CameraPanel(self.helper_frame)
        self.camera_panel = self.camera_panel_object.panel

        self.help_panel_object = HelpPanel(self.helper_frame)
        self.help_panel = self.help_panel_object.panel

        # Set Sashposition of the paned window
        self.paned_window.after(200, lambda: self.paned_window.sashpos(0, 840)) # after for short delay (bugfix)
        