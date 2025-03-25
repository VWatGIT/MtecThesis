import time

from Python_Skripts.GUI_Panels.Panel_Updates import * 
from Python_Skripts.GUI_Panels.Panel_Updates.update_gauss_beam import update_gauss_beam
from Python_Skripts.GUI_Panels.Movement_Procedures.do_measurement import doMeasurement

from Python_Skripts.Function_Groups.path_creation import generate_snake_path
from Python_Skripts.Function_Groups.data_handling import save_data



def run_measurements(root):
    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)
    data = tab.data


    # Get the grid size and step size
    root.grid_size = root.new_measurement_panel.nametowidget("input_frame").nametowidget('path_input_frame').nametowidget("measurement_space_entry").get()
    root.grid_size = tuple(map(float, root.grid_size.split(',')))

    root.step_size = root.new_measurement_panel.nametowidget("input_frame").nametowidget('path_input_frame').nametowidget("step_size_entry").get()
    root.step_size = tuple(map(float, root.step_size.split(',')))


    # Update Beam Parameters
    update_gauss_beam(root)


    # Get the Measurment points and path points
    tab.path_points, root.grid = generate_snake_path(root.grid_size, root.step_size)
    #root.log.log_event(f'Path Points: \n {tab.path_points}')

    add_3D_data(data, root.grid, root.grid_size, root.step_size, tab.path_points)
    root.log.log_event("Added 3D Data")

    tab.start_time = time.time()
    tab.elapsed_time = 0

    add_meta_data(root, data)

    tab.measurement_points = data["3D"]["measurement_points"]
    
    progress_bar = root.new_measurement_panel.nametowidget("progress_bar")
    progress_bar['maximum'] = tab.measurement_points
    
    # Start the measurement
    last_point = (0, 0, 0, 0, 0, 0) # Start at the origin
    

    for i in range(tab.measurement_points):
        if root.measurement_running is False:
            root.log.log_event("Measurement stopped")
            break

        # As Path points are absolute, transform them to relative positions
        next_point = (tab.path_points[i][0], tab.path_points[i][1], tab.path_points[i][2], 0, 0, 0) 
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        
        rcv = root.hexapod.move(next_relative_position, flag = "relative", simulate = root.simulate_var.get())
      
        last_point = next_point # Update the last point

        doMeasurement(root, data, root.sensor, root.hexapod, i)
        tab.measurement_id_var.set(i)



        # update only every ~10% of measurements to save time by not updating the UI every step
        update_interval = tab.measurement_points // 10
        if i%update_interval == 0:
            
            if i > 0 or i == tab.measurement_points - 1:
                root.log.delete_last_event()
                root.log.log_event(rcv)
                root.log.delete_last_event()
                root.log.log_event(f"Performed measurement: {i+1} / {tab.measurement_points}")

            else:   
                root.log.log_event(rcv)
                root.log.log_event(f"Performed measurement: {i+1} / {tab.measurement_points}")



            update_tab(root)
            update_progress_bar(root)
            tab.elapsed_time = int((time.time() - tab.start_time)/60)
            data["info"]["elapsed_time"] = tab.elapsed_time
            

        tab.elapsed_time = int((time.time() - tab.start_time)/60)
        data["info"]["elapsed_time"] = tab.elapsed_time

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
