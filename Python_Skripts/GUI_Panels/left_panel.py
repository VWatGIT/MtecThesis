import tkinter as tk

from Python_Skripts.GUI_Panels.home_panel import HomePanel
from Python_Skripts.GUI_Panels.new_measurement_panel import NewMeasurementPanel
from Python_Skripts.GUI_Panels.load_measurement_panel import LoadMeasurementPanel

class LeftPanel:
    def __init__(self, parent, root):
        self.root = root

        self.frame = tk.Frame(parent, width=340) # change "width"(340 was old default) depending on needed menu size
        self.root.left_panel = self.frame

        home_panel = HomePanel(self.frame, root).frame
        new_measurement_panel = NewMeasurementPanel(self.frame, root).panel
        load_measurement_panel = LoadMeasurementPanel(self.frame, root).frame
      

