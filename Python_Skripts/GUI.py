import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import pprint
import cv2
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pypylon.pylon as pylon
import os
import time

from Function_Groups.marker_detection import detect_markers
from Testing_Scripts.Beam_Trajectory import calculate_alpha_beta
from Testing_Scripts.Beam_Trajectory import plot_alpha_beta

# TODO fix module imports
from GUI_Panels import *
from Function_Groups import *

from Function_Groups.object3D import *
from Python_Skripts.Function_Groups.gauss_beam import GaussBeam
from Function_Groups.camera import Camera



class UserInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Probe Beam Measurement")
        self.root.geometry("1920x1080")
        self.root.wm_state("zoomed")

        # attach all global stuff to root
        self.root.camera_object = Camera() # camera = self.root.camera_object.camera
        self.root.sensor = Sensor()
        self.root.probe = Probe()
        self.root.hexapod = Hexapod()
        self.root.gauss_beam = GaussBeam() # Simulation Beam
        self.root.log = None
        self.root.camera_plot_frame = None

        measurement_running = False
        self.root.measurement_running = measurement_running

        # Create the TOP level GUI Elements with root as parent
        menu = create_menu(self.root)
        left_panel = LeftPanel(self.root, self.root).frame # includes home, new_measurement, load_measurement
        paned_window = PanedWindow(self.root, self.root).paned_window

        show_home_panel()
        show_camera_panel()



if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()