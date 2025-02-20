def update_tab(self, event=None):
    # TODO tab group has to be found in the root
    tab_name = self.tab_group.select()
    tab = self.root.nametowidget(tab_name)

    data = tab.data

    subtab_group = tab.nametowidget("subtab_group")
    sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")

    measurement_slider = sensor_path_frame.nametowidget("sensor_info_frame").nametowidget("measurement_slider")
    self.current_measurement_id = str(measurement_slider.get())

    self.update_sensor_info_frame()
    self.update_path_plot()

    if data['Visualization']["Slices"] != {}:
        self.update_slice_plot()
