import tkinter as tk
from tkinter import ttk

from Python_Skripts.GUI_Panels.manual_adjust_panel import ManualAdjustPanel
from Python_Skripts.GUI_Panels.Movement_Procedures.alignment import manual_alignment

class HelpPanel:
    def __init__(self, parent, root):
        self.panel = tk.Frame(parent, name="help_panel")
        
        self.root = root
        self.root.help_panel = self.panel
