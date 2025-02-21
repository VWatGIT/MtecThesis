import tkinter as tk
from tkinter import ttk

from GUI_Panels.manual_adjust_panel import ManualAdjustPanel
from Function_Groups.alignment import manual_alignment

class HelpPanel:
    def __init__(self, parent, root):
        self.panel = tk.Frame(parent, name="help_panel")
        
        self.root = root
        self.root.help_panel = self.panel

        # Move this somewhere else
        manual_adjust_panel = ManualAdjustPanel(self.panel, manual_alignment).panel
        manual_adjust_panel.pack(side="left", expand=True)
