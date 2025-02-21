import tkinter as tk


from Function_Groups.object3D import Probe, Sensor, Hexapod
from Function_Groups.gauss_beam import GaussBeam
from Function_Groups.camera import Camera

from GUI_Panels.top_panel import create_top_panel

from configparser import ConfigParser
import os


class UserInterface:
    def __init__(self, root):
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
        

        # Create the TOP level GUI Elements with root as parent
        self.top_panel = create_top_panel(root)


    def load_config(self):
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_path)

        self.root.grid_size = list(map(int, config.get('Measurement', 'grid_size').split(',')))
        self.root.step_size = list(map(int, config.get('Measurement', 'step_size').split(',')))
        self.root.num_calibration_images = int(config.get('Camera', 'num_calibration_images'))

if __name__ == "__main__":
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()