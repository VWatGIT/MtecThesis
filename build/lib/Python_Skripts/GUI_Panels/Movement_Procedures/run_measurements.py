import time

from Python_Skripts.GUI_Panels.Panel_Updates import * 
from Python_Skripts.GUI_Panels.Movement_Procedures.do_measurement import doMeasurement

from Python_Skripts.Function_Groups.path_creation import generate_snake_path
from Python_Skripts.Function_Groups.data_handling import save_data
from Python_Skripts.Function_Groups.beam_visualization import process_slices

def run_measurements(root):
    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)
    data = tab.data


    # Get the grid size and step size
    root.grid_size = root.new_measurement_panel.nametowidget("input_frame").nametowidget("measurement_space_entry").get()
    root.grid_size = tuple(map(float, root.grid_size.split(',')))

    root.step_size = root.new_measurement_panel.nametowidget("input_frame").nametowidget("step_size_entry").get()
    root.step_size = tuple(map(float, root.step_size.split(',')))


    # Get Beam Parameters
    theta = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("theta_entry").get())
    phi = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("phi_entry").get())
    root.gauss_beam.set_Trj(theta, phi)

    root.gauss_beam.w_0 = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("w_0_entry").get())*1e-3
    root.gauss_beam.wavelength = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("wavelength_entry").get())*1e-9
    root.gauss_beam.I_0 = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("i_0_entry").get())
    

    # Get the Measurment points and path points
    tab.path_points, root.grid = generate_snake_path(root.grid_size, root.step_size)
    #root.log.log_event(f'Path Points: \n {tab.path_points}')

    add_3D_data(data, root.grid, root.grid_size, root.step_size, tab.path_points)
    root.log.log_event("Added 3D Data")

    tab.start_time = time.time()
    tab.elapsed_time = 0

    add_meta_data(root, data)

    tab.measurement_points = data["3D"]["measurement_points"]
    #TODO set measurement slider maximum to measurement_points

    # Update the UI
    subtab_group = tab.nametowidget("subtab_group")


    progress_bar = root.new_measurement_panel.nametowidget("progress_bar")
    progress_bar['maximum'] = tab.measurement_points
    
    # Start the measurement
    last_point = (0, 0, 0, 0, 0, 0) # Start at the origin
    

    for i in range(tab.measurement_points):
        #root.log.log_event(f"Measurement {i+1} of {tab.measurement_points}")

        # As Path points are absolute, transform them to relative positions
        next_point = (tab.path_points[i][0], tab.path_points[i][1], tab.path_points[i][2], 0, 0, 0) 
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        
        #root.log.log_event(f"Next Relative Position: {next_relative_position}")
        
        if root.hexapod.connection_status is True:
            root.hexapod.move(next_relative_position, flag = "relative") 

        last_point = next_point # Update the last point

        doMeasurement(root, data, root.sensor, root.hexapod, i)
 
        tab.measurement_id_var.set(i)

        if i > 0: # TODO make this work
            #root.event_log.delete("end-2l", "end-1l")
            #root.event_log.insert("end-1l", f"Performed measurement {i+1} / {tab.measurement_points}\n")
            root.log.log_event(f"Performed measurement {i+1} / {tab.measurement_points}")
        else:
            root.log.log_event(f"Performed measurement {i+1} / {tab.measurement_points}")

        # update only every ~10% of measurements to save time by not updating the UI every step
        update_interval = tab.measurement_points // 10
        if i%update_interval == 0:

            update_tab(root)
            update_progress_bar(progress_bar, i+1)
            tab.elapsed_time = int((time.time() - tab.start_time)/60)
            data["info"]["elapsed_time"] = tab.elapsed_time
            

        tab.elapsed_time = int((time.time() - tab.start_time)/60)
        data["info"]["elapsed_time"] = tab.elapsed_time

    root.new_measurement_panel.nametowidget("save_button").config(state="normal")
    root.log.log_event("Done with measurements")     

    if root.hexapod.connection_status is True:
        root.hexapod.move_to_default_position() 
        root.log.log_event("Moved Hexapod to default position")
        
    root.log.log_event("Starting data processing")
    process_data(root, data)
    root.log.log_event(f"Finished data processing")

    # Final Update
    # Set Slider limits
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)
    subtab_group = tab.nametowidget("subtab_group")
    subtab_group.select(subtab_group.nametowidget("results_frame"))
    

    vertical_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("vertical_slice_slider")
    vertical_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['vertical']), state="normal")

    horizontal_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("slice_plot_frame").nametowidget("horizontal_slice_slider")
    horizontal_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['horizontal']), state="normal")

    update_tab(root)
    update_progress_bar(progress_bar,tab.measurement_points)
    update_beam_plot(root)
    update_measurement_info_frame(root)

    # autosave data
    if root.autosave_var.get() == 1:
        root.log.log_event("Autosaving data")
        # TODO make this a user input
        folder_path = 'C:/Users/mtec/Desktop/Thesis_Misc_Valentin/Git_repository/MtecThesis/Python_Skripts/experiment_data'
        probe_name = str(root.probe_name_entry.get())
        file_path = save_data(folder_path, data, probe_name)
        root.log.log_event("Data saved automatically to:" + file_path)

    root.measurement_running = False # end threading


def process_data(root, data):
    root.log.log_event("Processing data")
    process_slices(data)
    root.log.log_event("Created Slices and Beam Model")

# UTILITIES
def add_meta_data(root, data):
    data["camera"] = {
        
        "ret": root.camera_object.ret,
        "mtx": root.camera_object.mtx,
        "dist": root.camera_object.dist,
        "rvecs": root.camera_object.rvecs,
        "tvecs": root.camera_object.tvecs
    }

    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)

    data["info"] = {
        "name" : tab_name,
        "time_estimated": tab.time_estimated,
        "elapsed_time": tab.elapsed_time,
        "start_time": tab.start_time
    }

def add_3D_data(data, grid, grid_size, step_size, path):
    data["3D"] = {
        "grid": grid, # (X, Y, Z)
        "X": grid[0],
        "Y": grid[1],
        "Z": grid[2],
        "grid_size": grid_size,
        "step_size": step_size,
        "path": path, 
        "measurement_points": len(path)
    } 
