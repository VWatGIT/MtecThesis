import tkinter as tk
from configparser import ConfigParser
import os

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
        self.root.title("Probe Beam Measurement")
        self.root.geometry("1920x1080")
        #self.root.wm_state("zoomed")

        # attach all global stuff to root
        self.root.camera_object = Camera() # camera = self.root.camera_object.camera
        self.root.camera = self.root.camera_object.camera
        self.root.sensor = Sensor()
        self.root.probe = Probe()
        self.root.hexapod = Hexapod()
        self.root.gauss_beam = GaussBeam() # Simulation Beam
        self.root.log = None
        self.root.camera_plot_frame = None

        measurement_running = False
        self.root.measurement_running = measurement_running
        self.root.measurement_points = None
        self.root.current_measurement_id = 0
        self.root.path_points = None

        self.root.measurement_id_var = tk.IntVar()
        self.root.measurement_id_var.set(0)

        # TODO implement time estimation
        self.root.time_estimated = 0
        self.root.elapsed_time = 0
        self.root.start_time = 0
        
        self.load_config()


        # Create the TOP level GUI Elements with root as parent
        if not test_mode:
            self.top_panel = create_top_panel(root)
        else:
            # no panel craeated, only fully initialized root
            # used to test individual panels
            root.log = EventLogPanel(root, root)
            root.log.panel.pack(side="bottom", fill="both", expand=True)
            pass




    def load_config(self):
        config = ConfigParser()
        path = r"C:\Users\Valentin\Documents\GIT_REPS\MtecThesis\Python_Skripts\config.ini"
        config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
        config.read(config_path)

        #print(config_path)
        #print(config.sections())

        # Heapod/Probe/Sensor Configs set in Object3D

        self.root.grid_size = list(map(float, config.get('Measurement', 'grid_size').split(',')))
        self.root.step_size = list(map(float, config.get('Measurement', 'step_size').split(',')))

        self.root.num_calibration_images = tk.IntVar()

        self.root.camera_object.update_frequency = int(config.get('Camera', 'update_frequency'))
        self.root.max_num_calibration_images = int(config.get('Camera', 'max_num_calibration_images'))
        self.root.num_calibration_images.set(int(config.get('Camera', 'num_calibration_images')))
        self.root.checkerboard_size = int(config.get('Camera', 'checkerboard_size'))
        self.root.checkerboard_dims = tuple(map(int, config.get('Camera', 'checkerboard_dims').split(',')))

if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()