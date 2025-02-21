
from GUI_Panels.Panel_Updates.update_sensor_info_frame import update_sensor_info_frame
from GUI_Panels.Panel_Updates.update_path_plot import update_path_plot
from GUI_Panels.Panel_Updates.update_slice_plot import update_slice_plot

def update_tab(root, event=None):
    # TODO tab group has to be found in the root
    tab_name = root.tab_group.select()
    tab = root.nametowidget(tab_name)

    data = tab.data

    subtab_group = tab.nametowidget("subtab_group")
    sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
    measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
    root.current_measurement_id = str(measurement_slider.get())


    update_sensor_info_frame(root)
    update_path_plot(root)

    if data['Visualization']["Slices"] != {}:
        update_slice_plot(root)
