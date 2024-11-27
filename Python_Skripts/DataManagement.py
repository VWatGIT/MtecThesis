import os
import h5py
import numpy as np
from pylablib.devices import Thorlabs
from Object3D import Sensor, Probe

def save_data(data_folder, data):
    """
    Save the data to an HDF5 file.

    Parameters:
    data_folder (str): The folder to store the data.
    data (dict): The data to store, with keys for each measurement.
    """
    # Ensure the folder exists
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Define the HDF5 file path
    hdf5_file_path = os.path.join(data_folder, 'experiment_data.h5')

    # Write data to HDF5
    with h5py.File(hdf5_file_path, 'w') as hdf5_file:
        for key, value in data.items():
            key_str = str(key)  # Convert key to string
            if isinstance(value, (list, tuple)):
                value = np.array(value)  # Convert lists or tuples to numpy arrays
            if isinstance(value, dict):
                group = hdf5_file.create_group(key_str)
                for sub_key, sub_value in value.items():
                    sub_key_str = str(sub_key)
                    if isinstance(sub_value, (list, tuple)):
                        sub_value = np.array(sub_value)
                    if sub_value is not None:
                        group.create_dataset(sub_key_str, data=sub_value)
                    else:
                        print(f"Skipping None value for {sub_key_str}")
            else:
                if value is not None:
                    hdf5_file.create_dataset(key_str, data=value)
                else:
                    print(f"Skipping None value for {key_str}")

    print(f"Data saved to {hdf5_file_path}")

def load_data(hdf5_file_path):
    """
    Load the data from an HDF5 file.

    Parameters:
    hdf5_file_path (str): The path to the HDF5 file.

    Returns:
    dict: The loaded data.
    """
    with h5py.File(hdf5_file_path, 'r') as hdf5_file:
        data = {}
        for key in hdf5_file.keys():
            group = hdf5_file[key]
            if isinstance(group, h5py.Group):
                data[key] = {sub_key: group[sub_key][()] for sub_key in group.keys()}
            else:
                data[key] = group[()]
    return data

def doMeasurement(data, stage, sensor, probe):
    """
    Perform a measurement and store the results in the data dictionary.

    Parameters:
    data (dict): The data dictionary to store the results.
    stage: The stage object to perform the measurement.
    sensor: The sensor object.
    probe: The probe object.
    """
    stage.open()
    signal = stage.get_readings()
    signal_position = (signal.xpos, signal.ypos)
    signal_details = (signal.xdiff, signal.ydiff, signal.sum)
    stage.close()

    measurement_id = max(map(int, data.keys()), default=0) + 1
    measurement_id_str = str(measurement_id)  # Convert measurement_id to string
    data[measurement_id_str] = {
        'Signal_xpos': signal.xpos,
        'Signal_ypos': signal.ypos,
        'Signal_xdiff': signal.xdiff,
        'Signal_ydiff': signal.ydiff,
        'Signal_sum': signal.sum,
        'Sensor_position': sensor.position,
        'Sensor_rotation': sensor.rotation,
        'Probe_position': probe.position,
        'Probe_rotation': probe.rotation
    }

# Example usage
if __name__ == "__main__":
    # Define the folder to store the data
    data_folder = r'C:\Users\mtec\Desktop\Thesis_Misc_Valentin\Python_Skripts\Experiment_data'

    # Define the initial empty data structure
    data = {}

    # Add new measurements
    stage = Thorlabs.KinesisQuadDetector("69251980")
    sensor = Sensor()
    probe = Probe()

    doMeasurement(data, stage, sensor, probe)

    # Save the data
    save_data(data_folder, data)

    # Define the HDF5 file path
    hdf5_file_path = os.path.join(data_folder, 'experiment_data.h5')

    # Load the data
    loaded_data = load_data(hdf5_file_path)

    # Print the loaded data
    print("Loaded data:")
    print(loaded_data)