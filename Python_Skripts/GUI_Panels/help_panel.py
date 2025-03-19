import tkinter as tk
from tkinter import ttk

class HelpPanel:
    def __init__(self, parent, root):
        self.panel = tk.Frame(parent, name="help_panel")
        
        self.root = root
        self.root.help_panel = self.panel
