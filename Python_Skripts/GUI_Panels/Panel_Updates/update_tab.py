
from Python_Skripts.GUI_Panels.Panel_Updates.update_sensor_info_frame import update_sensor_info_frame
from Python_Skripts.GUI_Panels.Panel_Updates.update_path_plot import update_path_plot
from Python_Skripts.GUI_Panels.Panel_Updates.update_slice_plot import update_slice_plot

def update_tab(root, event=None):
    # TODO tab group has to be found in the root
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)

    data = tab.data

    update_sensor_info_frame(root)
    
    if root.measurement_running is True:
        update_path_plot(root)

    if data['Visualization']["Slices"] != {}:
        update_slice_plot(root)
