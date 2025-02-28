import os
import h5py
import time
from datetime import datetime
import numpy as np

def new_data(): 
    # Creates empty Data structure
    # attach this to the new tab
    data = {}
    data["3D"] = {}
    data["Measurements"] = {}
    data['Info'] = {}
    data['Visualization'] = {}
    data['Visualization']['Slices'] = {}
    data['Beam_Parameters'] = {}
    data['Alignment'] = {}
    data['Alignment']['Center_Search'] = {}
    data['Simulation'] = {}
    data['Simulation']["active"] = False
    return data

def save_data(data_folder, data, probe_name):

    # Ensure the folder exists
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    # Define the HDF5 file path
    date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    hdf5_file_path = os.path.join(data_folder, str(probe_name)+"_"+str(date)+'.h5')

    #convert data --> ensure that all data is in the correct format
    data = convert_data(data)
    #pprint.pprint(data)
    #self.print_data_with_types(data)

    # Recursive function to save nested dictionaries
    def save_group(group, data):
        for key, value in data.items():
            key_str = str(key)  # Convert key to string
            if isinstance(value, dict):
                if value:  # Check if the dictionary is not empty
                    subgroup = group.create_group(key_str)
                    save_group(subgroup, value)
                else:
                    print(f"Skipping empty dictionary for {key_str}")
            else:
                if value is not None:
                    group.create_dataset(key_str, data=value)
                else:
                    print(f"Skipping None value for {key_str}")


    # Write data to HDF5
    with h5py.File(hdf5_file_path, 'w') as hdf5_file:
        save_group(hdf5_file, data)
            
    return hdf5_file_path

def load_data(hdf5_file_path):
        # Recursive function to load nested dictionaries
        def load_group(group): 
            data = {}
            for key in group.keys():
                #print(f'{key} +{group[key]}')
                item = group[key]
                if isinstance(item, h5py.Group):
                    data[key] = load_group(item)
                else:
                    data[key] = item[()]

            return data


        with h5py.File(hdf5_file_path, 'r') as hdf5_file:
            data = load_group(hdf5_file)

        return data

def autosave(root):
    data = root.tab_group.nametowidget(root.tab_group.select()).data

    # autosave data
    if root.autosave_var.get() == 1:
        root.log.log_event("Autosaving data")
        # TODO make this a user input
        folder_path = 'C:/Users/mtec/Desktop/Thesis_Misc_Valentin/Git_repository/MtecThesis/Python_Skripts/experiment_data'
        probe_name = str(root.probe_name_entry.get())
        file_path = save_data(folder_path, data, probe_name)
        root.log.log_event("Data saved automatically to:" + file_path)

def convert_data(data):
    try:
        if isinstance(data, dict):
            return {key: convert_data(value) for key, value in data.items()}
        elif isinstance(data, (list, tuple)):
            return np.array(data, dtype=np.float64)  # Convert lists or tuples to numpy arrays of floats
        elif isinstance(data, np.ndarray):
            if data.dtype == object or data.dtype.kind in {'i', 'u'}:
                #print(f"object array: {data}") # Convert object arrays to float arrays
                return data.astype(np.float64)
            else:
                return data
        else:
            return data
    except TypeError as e:
        print(f"Error converting data: {e}")
        print(f"Type of data: {type(data)}, dtype: {data.dtype if isinstance(data, np.ndarray) else 'N/A'}")
        raise