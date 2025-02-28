import numpy as np
import matplotlib.pyplot as plt

from Python_Skripts.Function_Groups.path_creation import generate_snake_path
from Python_Skripts.Function_Groups.trajectory import refine_search

from Python_Skripts.GUI_Panels.Panel_Updates.update_gauss_beam import update_gauss_beam

def find_beam_centers(root):
     #TODO decide on center_spacing and number of centers         
    # 2D search for beam center (one slice)
    # Assuming the beam center has the maximal intensity
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data

    # update gauss beam
    update_gauss_beam(root)

    num_centers = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget("num_centers_entry").get())
    center_spacing = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("center_spacing_entry").get())
    initial_step_size = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("initial_step_size_entry").get())
    refinement_factor = float(root.new_measurement_panel.nametowidget("input_frame").nametowidget("refinement_factor_entry").get())
    max_num_iterations = int(root.new_measurement_panel.nametowidget("input_frame").nametowidget("max_num_iterations_entry").get())


    data['Alignment']['Center_Search']['Beam_Centers'] = []
    data['Alignment']['Center_Search']['Path_Points'] = []


    step_size = (center_spacing, 1, 1)
    grid_size = ((num_centers-1)*center_spacing,0 , 0)

    x_path_points, _ = generate_snake_path(grid_size, step_size)    
    print(f'Path Points: \n {x_path_points}')

    for i in range(len(x_path_points)):
        root.log.log(f'Searching for center {i+1}/{num_centers}')

        last_point = root.hexapod.position
        next_point = (x_path_points[i][0], x_path_points[i][1], x_path_points[i][2], 0, 0, 0)
        next_relative_position = (next_point[0] - last_point[0], next_point[1] - last_point[1], next_point[2] - last_point[2], 0, 0, 0)
        root.hexapod.move(next_relative_position, flag = "relative")

        center, all_path_points = refine_search(root.hexapod.position, initial_step_size, refinement_factor, max_num_iterations)
        
        root.log.log_event(f'Center {i+1}/{num_centers} found at {center}')

        data['Alignment']['Center_Search']['Path_Points'].append(all_path_points)
        data['Alignment']['Center_Search']['Beam_Centers'].append(center)
    
        
        
    plt.show()

    return data


if __name__ == "__main__":
    from Python_Skripts.GUI import UserInterface
    from Python_Skripts.GUI_Panels.beam_center_plot_frame import BeamCenterPlotFrame
    from Python_Skripts.GUI_Panels.Panel_Updates.update_gauss_beam import update_gauss_beam
    from Python_Skripts.GUI_Panels.Panel_Updates.update_beam_center_plot import update_beam_center_plot

    import tkinter as tk
    root = tk.Tk()



    plot_panel = BeamCenterPlotFrame(root, root).panel

    root.mainloop