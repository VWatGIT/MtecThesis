import tkinter as tk
from tkinter import ttk

from datetime import datetime

class EventLogPanel:
    def __init__(self, parent, root):
        self.panel = tk.LabelFrame(parent, text="Event Log")
        self.panel.pack(side="right", fill="x", padx=10, pady=10)

        self.root = root
        self.root.event_log_panel = self.panel

        # Actual Log here
        self.event_log = tk.Text(self.panel, height = 5, width = 20, state='disabled')
        self.event_log.pack(expand =True, fill="both", padx=10, pady=10)

    def log_event(self, message):
        current_time = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{current_time}] {message}"
        self.event_log.config(state='normal')
        self.event_log.insert(tk.END, formatted_message + '\n')
        self.event_log.config(state='disabled')
        self.event_log.see(tk.END)
