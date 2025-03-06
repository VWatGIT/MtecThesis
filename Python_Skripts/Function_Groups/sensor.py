import os
import numpy as np
from configparser import ConfigParser


class Signal: # Dummy
    # signal class only used for testing purposes
    def __init__(self, xpos, ypos, xdiff, ydiff, sum):
        self.xpos = xpos
        self.ypos = ypos
        self.xdiff = xdiff
        self.ydiff = ydiff
        self.sum = sum

class Sensor():
    def __init__(self):
        # Load Configuration
        config = ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config.ini')
        config.read(config_path)

        self.marker_id = config.getint('Sensor', 'marker_id')
        self.marker_size = config.getfloat('Sensor', 'marker_size')

        self.marker_tvecs = [] 
        self.marker_rvecs = []

        self.marker_detected = False

         # 0 unique_rvecs if sicker is applied correctly
        # TODO measure unique_tvecs from marker corner to photo diode array

        self.unique_rvecs = list(map(float, config.get('Sensor', 'unique_rvecs').split(',')))
        self.unique_tvecs = list(map(float, config.get('Sensor', 'unique_tvecs').split(',')))

        self.photo_diode_array_position = None # in hexapod coordinates relative to camera position

        # Sensor Readings
        self.xpos = None
        self.ypos = None
        self.xdiff = None
        self.ydiff = None
        self.sum = None

        # initialize stage
        self.stage = None
        #self.initialize_stage()

    def set_marker_vecs(self, marker_tvecs, marker_rvecs):
        self.marker_tvecs = marker_tvecs
        self.marker_rvecs = marker_rvecs
        if marker_tvecs is not None and marker_rvecs is not None:
            self.marker_detected = True


    def initialize_stage(self, callback=None, root=None): 
        # initialize the stage

        """
        Expects callback function as input argument
        callback(rcv) is called after connection attempt
        """
        if callback is None:
            callback = lambda x: print(x)

        try:
            #self.stage = Thorlabs.KinesisQuadDetector("69251980") TODO uncomment
            x = "5" + 6  # TODO delete later only for error creation
            result = "Stage initialized sucessfully" # 
            callback(result)

        except Exception as e:
            self.stage = None
            result = f"Stage initialization failed: {e}"
            callback(result)
            pass
        
    def get_signal(self):
        if self.stage is None:
            return self.get_test_signal()
        else:
            self.stage.open() # TODO: improve performance
            signal = self.stage.get_readings()
            self.xpos = signal.xpos
            self.ypos = signal.ypos
            self.xdiff = signal.xdiff
            self.ydiff = signal.ydiff
            self.sum = signal.sum
            self.stage.close()
            return signal 

    def get_test_signal(self): # used for working at home
        self.xpos = (np.random.rand()-0.5)*10
        self.ypos = (np.random.rand()-0.5)*10
        self.xdiff = (np.random.rand()-0.5)*10
        self.ydiff = (np.random.rand()-0.5)*10
        self.sum = np.random.rand()*100
        test_signal = Signal(self.xpos, self.ypos, self.xdiff, self.ydiff, self.sum)  # return same data type as get_signal
        
        return test_signal


    def __repr__(self):
        return f"Sensor(position={self.position}, rotation={self.rotation})"
