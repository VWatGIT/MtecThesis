import numpy as np
import matplotlib.pyplot as plt

from Python_Skripts.Function_Groups.path_creation import generate_snake_path

from Python_Skripts.GUI_Panels.Panel_Updates.update_gauss_beam import update_gauss_beam
from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_center_plot import update_beam_center_plot

def find_beam_centers(root):
     #TODO decide on center_spacing and number of centers         
    # 2D search for beam center (one slice)
    # Assuming the beam center has the maximal intensity
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data

    # update gauss beam
    root.after(0, update_gauss_beam, root)
    #update_gauss_beam(root)

    num_centers = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget("num_centers_entry").get())
    center_spacing = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("center_spacing_entry").get())
    initial_search_area = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("initial_search_area_entry").get())
    refinement_factor = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("refinement_factor_entry").get())
    max_num_iterations = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget("max_num_iterations_entry").get())


    data['Alignment']['Center_Search']['Beam_Centers'] = []
    data['Alignment']['Center_Search']['Path_Points'] = []


    step_size = (center_spacing, 1, 1)
    grid_size = ((num_centers-1)*center_spacing,0 , 0)

    x_path_points, _ = generate_snake_path(grid_size, step_size)    
    #print(f'Path Points: \n {x_path_points}')

    for i in range(len(x_path_points)):
        root.log.log_event(f'Searching for center {i+1}/{num_centers}')

        last_point = root.hexapod.position
        next_point = (x_path_points[i][0], x_path_points[i][1], x_path_points[i][2], 0, 0, 0)
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        root.hexapod.move(next_relative_position, flag = "relative")

        center = refine_search(root, data, root.hexapod.position, initial_search_area, refinement_factor, max_num_iterations)
        
        root.log.log_event(f'Center {i+1}/{num_centers} found at {center}')

        data['Alignment']['Center_Search']['Beam_Centers'].append(center)


    return data['Alignment']['Center_Search']['Beam_Centers']



def grid_search(root, data, initial_point, grid_size, step_size):
    max_value = -np.inf
    max_point = None
    
    step_size = (step_size, step_size, step_size)

    path_points, _ = generate_snake_path(grid_size, step_size)

    # Transform path points to positions relative to the initial point
    for point in path_points:
        data['Alignment']['Center_Search']['Path_Points'].append((point[0] + initial_point[0], point[1] + initial_point[1], point[2] + initial_point[2]))

    #update_beam_center_plot(root)
    root.after(0, update_beam_center_plot, root)
    #print(f'Path Points: \n {path_points}')
    last_point = initial_point
    root.hexapod.move(initial_point, flag = "absolute")
    for i in range(len(path_points)):

        # As Path points are absolute, transform them to relative positions
        next_point = np.array((path_points[i][0] + initial_point[0], path_points[i][1] + initial_point[1], path_points[i][2] + initial_point[2], 0, 0, 0))
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        root.hexapod.move(next_relative_position, flag = "relative")
        last_point = next_point

        current_path_point = (root.hexapod.position[0], root.hexapod.position[1], root.hexapod.position[2])
        if root.simulate_var.get() == 1:
            value = root.gauss_beam.get_Intensity(point = current_path_point)

        signal = root.sensor.get_signal()
        value = signal.sum


        if value > max_value:
            max_value = value
            x = root.hexapod.position[0]
            y = root.hexapod.position[1]
            z = root.hexapod.position[2]
            max_point = (x, y, z)
            #print(f'new max value: {max_value:.2f} at {max_point}')
        

        tab = root.tab_group.nametowidget(root.tab_group.select())
        tab.current_point_index += 1
        #update_beam_center_plot(root)
        root.after(0, update_beam_center_plot, root)
    #print(f'finished iteration, new center: {max_point}')
    return max_point

def refine_search(root, data, initial_point, initial_search_area = 5, refinement_factor = 2, max_iterations = 3):
    step_size = 1
    initial_hexapod_position = initial_point
    center = initial_point
    
    for _ in range(max_iterations):
        # Hexapod moves along the path points, which are relative
        # range and grid_size are formatted in a way so it fits the path creation
        y_range = z_range = (-initial_search_area*step_size, initial_search_area*step_size) # 5 mm in each direction

        grid_size = (0, y_range[1] - y_range[0], z_range[1] - z_range[0])

        center = grid_search(root, data, center, grid_size, step_size)
        step_size /= refinement_factor

    root.hexapod.move(initial_hexapod_position, flag = "absolute") # return to initial position after finsished search

    return center


if __name__ == "__main__":
    from Python_Skripts.GUI_Panels.beam_center_plot_frame import BeamCenterPlotFrame

    import tkinter as tk
    root = tk.Tk()

    # TODO i dnt know how to properly test this without opening the main gui all the time
    plot_frame = BeamCenterPlotFrame(root, root).frame
    plot_frame.pack(side = "top", fill = "both", expand = True)

    button = tk.Button(root, text = "Find Beam Centers", command = lambda: find_beam_centers(root))
    button.pack(side = "bottom")

    root.mainloop()