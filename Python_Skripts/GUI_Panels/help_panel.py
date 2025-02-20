import tkinter as tk
from tkinter import ttk

from .manual_adjust_panel import ManualAdjustPanel
from Function_Groups.alignment import manual_alignment

class HelpPanel:
    def __init__(self, parent):
        self.help_panel = tk.Frame(parent, name="help_panel")
        

        # Move this somewhere else
        manual_adjust_panel = ManualAdjustPanel(self.help_panel, manual_alignment).panel
        manual_adjust_panel.pack(side="left", expand=True)
