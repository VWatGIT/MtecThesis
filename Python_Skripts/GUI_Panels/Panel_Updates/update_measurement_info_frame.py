def update_measurement_info_frame(root, event = None):
    
    # update labels here
    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)
    data = tab.data
    subtab_group = tab.nametowidget("subtab_group")
    measurement_info_frame = subtab_group.nametowidget("measurement_info_frame")

    general_info_frame = measurement_info_frame.nametowidget("general_info_frame")
    measurement_points_label = general_info_frame.nametowidget("measurement_points_label")
    grid_size_label = general_info_frame.nametowidget("grid_size_label")
    step_size_label = general_info_frame.nametowidget("step_size_label")
    time_elapsed_label = general_info_frame.nametowidget("time_elapsed_label")
    time_estimated_label = general_info_frame.nametowidget("time_estimated_label")

    measurement_points_label.config(text=f"Measurement Points: {data['3D']['measurement_points']}")
    step_size_label.config(text=f"Step Size: {data['3D']['step_size']}")
    grid_size_label.config(text=f"Grid Size: {data['3D']['grid_size']}")
    time_elapsed_label.config(text=f"Time Elapsed: {data['info']['elapsed_time']}")
    time_estimated_label.config(text=f"Time Estimated: {data['info']['time_estimated']}")

    laser_info_frame = measurement_info_frame.nametowidget("laser_info_frame")
    w_0_label = laser_info_frame.nametowidget("w_0_label")
    wavelength_label = laser_info_frame.nametowidget("wavelength")
    i_0_label = laser_info_frame.nametowidget("i_0_label")
    z_r_label = laser_info_frame.nametowidget("z_r_label")
    pitch_label = laser_info_frame.nametowidget("pitch_label")
    yaw_label = laser_info_frame.nametowidget("yaw_label")

    # TODO update correctly
    #pitch_label.config(text=f"Pitch: {data['Visualization']['Beam_Models']['Measured_Beam']['theta']:.2f}")
    #yaw_label.config(text=f"Yaw: {data['Visualization']['Beam_Models']['Measured_Beam']['phi']:.2f}")