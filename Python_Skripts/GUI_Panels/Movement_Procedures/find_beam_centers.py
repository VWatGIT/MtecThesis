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
    root.after(10, update_gauss_beam, root)
    #update_gauss_beam(root)

    num_centers = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("num_centers_entry").get())
    center_spacing = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("center_spacing_entry").get())
    initial_search_area = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("initial_search_area_entry").get())
    initial_step_size = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("initial_step_size_entry").get())
    refinement_factor = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("refinement_factor_entry").get())
    max_num_iterations = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget('center_search_input_frame').nametowidget("max_num_iterations_entry").get())


    data['Alignment']['Center_Search']['Beam_Centers'] = []
    data['Alignment']['Center_Search']['Path_Points'] = []


    step_size = (center_spacing, 1, 1)
    grid_size = ((num_centers-1)*center_spacing,0 , 0)

    x_path_points, _ = generate_snake_path(grid_size, step_size)    

    aligned_position = root.hexapod.get_position(simulate = root.simulate_var.get())
     
    for i in range(len(x_path_points)):
        if root.measurement_running == False:
            root.log.log_event(f'Terminating center search at center {i+1}/{num_centers}')
            break

        root.log.log_event(f'Searching for center {i+1}/{num_centers}')

        last_position = root.hexapod.get_position(simulate = root.simulate_var.get())

        next_point = (x_path_points[i][0], x_path_points[i][1], x_path_points[i][2])
        new_position = (last_position[0] + next_point[0],last_position[1] + next_point[1],last_position[2] + next_point[2], 0, 0, 0)
        root.hexapod.move(new_position, flag = "absolute", simulate = root.simulate_var.get())
        print(f"new plane: {root.hexapod.get_position(simulate = root.simulate_var.get())}")
        current_slice_position = root.hexapod.get_position(simulate = root.simulate_var.get())

        if root.center_search_method_var.get() == 'quadrant':
            center = quadrant_search(root, data, next_point, initial_search_area, max_num_iterations)
            root.hexapod.move(current_slice_position, flag = "absolute", simulate = root.simulate_var.get()) # move back to the current position as quadrant search moves the hexapod
        elif root.center_search_method_var.get() == 'refine':
            center = refine_search(root, data, next_point, initial_search_area, initial_step_size, refinement_factor, max_num_iterations)
            root.hexapod.move(current_slice_position, flag = "absolute", simulate = root.simulate_var.get()) # move back to the current position as refine search moves the hexapod
            print(f"moved back: {root.hexapod.get_position(simulate = root.simulate_var.get())}")

        if np.isclose(np.abs(center[1]), abs(initial_search_area), rtol = 1e-3, atol = 1e-3) or np.isclose(np.abs(center[2]), abs(initial_search_area), rtol = 1e-3, atol = 1e-3):
            root.log.log_event(f'Center {i+1}/{num_centers} not found, search area too small')
        else:
            data['Alignment']['Center_Search']['Beam_Centers'].append(center)
            root.log.log_event(f'Center {i+1}/{num_centers} found at {center}')


    root.after(10, update_beam_center_plot, root)
    
    return data['Alignment']['Center_Search']['Beam_Centers']


def refine_search(root, data, initial_point, initial_search_area = 5, initial_step_size = 1, refinement_factor = 2, max_iterations = 3):
    # TODO fix
    def grid_search(root, data, current_center, grid_size, step_size):
        if root.measurement_running == False:
            return current_center
        
        max_value = -np.inf
        max_point = None
        
        step_size = (step_size, step_size, step_size)

        path_points, _ = generate_snake_path(grid_size, step_size)

        # Transform path points to positions relative to the initial point
        for point in path_points:
            data['Alignment']['Center_Search']['Path_Points'].append((point[0] + current_center[0], point[1] + current_center[1], point[2] + current_center[2]))

        #update_beam_center_plot(root)
        root.after(10, update_beam_center_plot, root)
        #print(f'Path Points: \n {path_points}')
   
        current_slice_position = root.hexapod.get_position(simulate = root.simulate_var.get())
        for i in range(len(path_points)):

            # As Path points are absolute, transform them to relative positions
            next_point = np.array((path_points[i][0] + current_center[0], path_points[i][1] + current_center[1], path_points[i][2] + current_center[2]))
            
            new_position = (current_slice_position[0] + next_point[0],current_slice_position[1] + next_point[1],current_slice_position[2] + next_point[2], 0, 0, 0)
            root.hexapod.move(new_position, flag = "absolute", simulate = root.simulate_var.get())
          
            if root.simulate_var.get() == True:
                value = root.gauss_beam.get_Intensity(point = path_points[i])
            else:
                signal = root.sensor.get_signal()
                value = signal.sum


            if value > max_value:
                max_value = value
                max_point = (current_center[0] + path_points[i][0], current_center[1] + path_points[i][1], current_center[2] + path_points[i][2])

            tab = root.tab_group.nametowidget(root.tab_group.select())
            tab.current_point_index += 1
            #update_beam_center_plot(root)

            #root.after(10, update_beam_center_plot, root)
        #print(f'finished iteration, new center: {max_point}')
        return max_point

    
    step_size = initial_step_size

    # Scale to allow for the first search area to not be greater than the initial search area
    # due to being multiplied by the step size which gets divided by the refinement factor later
    scaled_area = initial_search_area/step_size
    
    center = tuple(initial_point)
    for _ in range(max_iterations):
        if root.measurement_running == False:
            return center
        
        # Hexapod moves along the path points, which are relative
        # range and grid_size are formatted in a way so it fits the path creation
        y_range = z_range = (-scaled_area*step_size, scaled_area*step_size) # 5 mm in each direction

        grid_size = (0, y_range[1] - y_range[0], z_range[1] - z_range[0])

        center = grid_search(root, data, center, grid_size, step_size)
        #print(f'Center found: {center} in iteration {_}')
        step_size /= refinement_factor

    return center


def quadrant_search(root, data, current_center, initial_search_area, max_iterations):
    """ 
    recursive function
    returns the center in a plane as a tuple (x, y, z)
    moves the hexapod to that point
    """
    if root.measurement_running == False:
        return current_center

    # define the 4 points to measure relative to the initial point
    top_left = (current_center[0], current_center[1] - initial_search_area, current_center[2] + initial_search_area)
    top_right = (current_center[0], current_center[1] + initial_search_area, current_center[2] + initial_search_area)
    bottom_left = (current_center[0], current_center[1] - initial_search_area, current_center[2] - initial_search_area)
    bottom_right = (current_center[0], current_center[1] + initial_search_area, current_center[2] - initial_search_area)

    points = [top_left, top_right, bottom_right, bottom_left] # maybe include top_left again to build a rectangle?
    data['Alignment']['Center_Search']['Path_Points'].extend(points)
    root.after(0, update_beam_center_plot, root)
    tab = root.tab_group.nametowidget(root.tab_group.select())

    # measure the points
    values = []
    start_position = root.hexapod.get_position(simulate = root.simulate_var.get())
    print(f"start_position {start_position}")

    for point in points:
        if root.measurement_running == False:
            return current_center
        
    
        next_position = (start_position[0] + point[0],start_position[1] + point[1],start_position[2] + point[2], 0, 0, 0)
        root.hexapod.move(next_position, flag = "absolute", simulate = root.simulate_var.get())
        #data['Alignment']['Center_Search']['Path_Points'].append(point)

        if root.simulate_var.get() == True:
            # change point to laser coordinates
            value = root.gauss_beam.get_Intensity(point = point)#, shift = [0, -1, +2]) # example shift
        else:      
            value = root.sensor.get_signal().sum
        values.append(value)

        # Update the beam center plot
        tab.current_point_index += 1
        root.after(0, update_beam_center_plot, root)
        

    # now determine the new_center of the quadrant with the max_point in it
  

    # now find the center of the rectangle built by the point and center with the smallest difference
    max_point = points[np.argmax(values)]
    new_center = None
    # set the new center to the midpoint of the rectangle 
    new_center = [current_center[0], current_center[1] + (max_point[1] - current_center[1])/2, current_center[2] + (max_point[2] - current_center[2])/2]
    
    if new_center is None:
        root.log.log_event("No new center found")
        return current_center

    max_iterations -= 1
    if max_iterations == 0:
        return new_center

    if np.all(np.isclose(current_center[:3], new_center, rtol = 1e-3, atol = 1e-3)):
        return new_center
    else:
        # move the hexapod to the new center
        root.hexapod.move(start_position, flag = "absolute", simulate = root.simulate_var.get())
        delta_position = (new_center[0] - current_center[0], new_center[1] - current_center[1], new_center[2] - current_center[2], 0, 0, 0)
        print(f"after 4 points hexapod position {root.hexapod.get_position(root.simulate_var.get())}")
        print(f"delta position: {delta_position}")
        root.hexapod.move(delta_position, flag = "relative", simulate = root.simulate_var.get())
        print(f"after delta hexapod position {root.hexapod.get_position(root.simulate_var.get())}")
        print("\n")
        return quadrant_search(root, data, new_center, initial_search_area/2, max_iterations)




if __name__ == "__main__":
    from Python_Skripts.GUI_Panels.beam_center_plot_frame import BeamCenterPlotFrame
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    import tkinter as tk
    
    