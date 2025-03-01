from Python_Skripts.Function_Groups.beam_visualization import process_slices
from Python_Skripts.GUI_Panels.Panel_Updates import *


from Python_Skripts.Function_Groups.trajectory import calculate_beam_trajectory_LR, calculate_angles

def process_beam_centers(root):
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data

    centers = data['Alignment']['Center_Search']['Beam_Centers']

    trj = calculate_beam_trajectory_LR(centers)
    angles = calculate_angles(trj)

    data['Alignment']['Center_Search']['trajectory'] = trj
    data['Alignment']['Center_Search']['angles'] = angles

    return trj, angles

def process_data(root):
  
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)
    data = tab.data


    process_slices(data)
    root.log.log_event("Created Slices and Beam Model")

    # Update after processing
    # Set Slider limits
    
    subtab_group = tab.nametowidget("subtab_group")
    subtab_group.select(subtab_group.nametowidget("results_frame"))
    

    vertical_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("vertical_slice_plot_frame").nametowidget('helper_frame').nametowidget("vertical_slice_slider")
    vertical_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['vertical']), state="normal")

    horizontal_slice_slider = subtab_group.nametowidget("results_frame").nametowidget("horizontal_slice_plot_frame").nametowidget('helper_frame').nametowidget("horizontal_slice_slider")
    horizontal_slice_slider.config(from_=1, to=len(data['Visualization']["Slices"]['horizontal']), state="normal")

    update_tab(root)
    update_progress_bar(root)
    update_beam_plot(root)
    update_measurement_info_frame(root)