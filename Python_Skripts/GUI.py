import tkinter as tk
from configparser import ConfigParser
import os
import sys
import numpy as np

from Python_Skripts.Function_Groups.hexapod import Hexapod
from Python_Skripts.Function_Groups.probe import Probe
from Python_Skripts.Function_Groups.sensor import Sensor

from Python_Skripts.Function_Groups.gauss_beam import GaussBeam
from Python_Skripts.Function_Groups.camera import Camera

from Python_Skripts.GUI_Panels.top_panel import create_top_panel
from Python_Skripts.GUI_Panels.event_log_panel import EventLogPanel



class UserInterface:
    def __init__(self, root, test_mode=False):
        self.root = root

        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        root.stop_threads = False
        root.thread_list = []

        # attach all global stuff to root
        root.camera_object = Camera() # camera = root.camera_object.camera
        root.camera = root.camera_object.camera
        root.sensor = Sensor()
        root.probe = Probe()
        root.hexapod = Hexapod()
        root.gauss_beam = GaussBeam() # Simulation Beam
        root.log = None
        root.camera_plot_frame = None
        root.camera_object.updating = False
        root.measurement_running = False
        root.stop_update_checkboxes = False
        root.simulate_var = tk.IntVar(value = 0)
        root.quadrant_search_var = tk.BooleanVar(value = True)

        self.load_config()


        # Create the TOP level GUI Elements with root as parent
        if not test_mode:
            root.title("Probe Beam Measurement")
            root.geometry("1920x1080")
            #root.wm_state("zoomed")
            self.top_panel = create_top_panel(root)
            
            root.checkbox_panel_object.connect_hexapod()
            root.checkbox_panel_object.connect_stage()

        else:
            # no panel craeated, only fully initialized root
            # used to test individual panels
            
            root.log = EventLogPanel(root, root)
            root.log.panel.pack(side="bottom", fill="both", expand=True)
            pass
    

    def on_closing(self):
        self.root.camera_object.updating = False
        self.root.stop_update_checkboxes = True
        self.root.stop_threads = True
        self.measurement_running = False
        
        """
        for thread in self.root.thread_list:
            thread.join()
        """
        self.root.destroy()
        sys.exit()

    def load_config(self):
        config = ConfigParser()
        #path = r"C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\config.ini"
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
        config.read(config_path)

        # Heapod/Probe/Sensor Configs set in Object3D
        self.root.grid_size = list(map(float, config.get('Measurement', 'grid_size').split(',')))
        self.root.step_size = list(map(float, config.get('Measurement', 'step_size').split(',')))
        self.root.center_spacing = float(config.get('Measurement', 'center_spacing'))
        self.root.num_centers = int(config.get('Measurement', 'num_centers'))
        self.root.initial_search_area = float(config.get('Measurement', 'initial_search_area'))
        self.root.initial_step_size = float(config.get('Measurement', 'initial_step_size'))
        self.root.refinement_factor = float(config.get('Measurement', 'refinement_factor'))
        self.root.max_num_iterations = int(config.get('Measurement', 'max_num_iterations'))


        self.root.camera_object.num_calibration_images = tk.IntVar(value=int(config.get('Camera', 'num_calibration_images')))
        self.root.camera_object.max_num_calibration_images = int(config.get('Camera', 'max_num_calibration_images'))
        self.root.camera_object.default_mtx = np.array(list(map(float, config.get('Camera', 'default_mtx').split(',')))).reshape(3,3)
        self.root.camera_object.default_dist = np.array(list(map(float, config.get('Camera', 'default_dist').split(','))))
        self.root.camera_object.update_frequency = int(config.get('Camera', 'update_frequency'))
        self.root.camera_object.checkerboard_size = int(config.get('Camera', 'checkerboard_size'))
        self.root.camera_object.checkerboard_dimensions = tuple(map(int, config.get('Camera', 'checkerboard_dimensions').split(',')))

        # TODO maybe also load config for Hexapod/Probe/Sensor here


        
if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()