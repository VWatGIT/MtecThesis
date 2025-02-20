import tkinter as tk
from home_panel import HomePanel
from new_measurement_panel import NewMeasurementPanel
from load_measurement_panel import LoadMeasurementPanel

class LeftPanel:
    def __init__(self, parent, root):
        self.root = root

        self.frame = tk.Frame(parent, width=340) # change "width" depending on needed menu size
        self.frame.pack(side="left", fill="both")

        home_panel = HomePanel(self.frame).frame
        new_measurement_panel = NewMeasurementPanel(self.frame).panel
        load_measurement_panel = LoadMeasurementPanel(self.frame).frame
      

