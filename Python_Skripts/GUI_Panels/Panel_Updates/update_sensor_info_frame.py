def update_sensor_info_frame(root, event = None):
    tab_name = root.tab_group.select()
    tab = root.tab_group.nametowidget(tab_name)
    data = tab.data

    subtab_group = tab.nametowidget("subtab_group")
    results_frame = subtab_group.nametowidget("results_frame")
    sensor_info_frame = results_frame.nametowidget("sensor_info_frame")
    sensor_readings_frame = sensor_info_frame.nametowidget("sensor_readings_frame")

    current_measurement_data = data["Measurements"][str(root.measurement_slider_var.get())]

    sensor_info_frame.config(text="Measurement " + str(root.measurement_slider_var.get()) + "/" + str(tab.measurement_points)) # Update the title

    measurement_slider = sensor_info_frame.nametowidget("measurement_slider")
    if tab.measurement_points != measurement_slider.config()["to"][4]:
       measurement_slider.config(from_=1, to= int(tab.measurement_points)) # Update the slider range

    # Update the sensor readings
    xpos_label = sensor_readings_frame.nametowidget("xpos_label")
    ypos_label = sensor_readings_frame.nametowidget("ypos_label")
    xdiff_label = sensor_readings_frame.nametowidget("xdiff_label")
    ydiff_label = sensor_readings_frame.nametowidget("ydiff_label")
    sum_label = sensor_readings_frame.nametowidget("sum_label")

    xpos_label.config(text=f"X Position: {current_measurement_data['Signal_xpos']:.2f}")
    ypos_label.config(text=f"Y Position: {current_measurement_data['Signal_ypos']:.2f}")
    xdiff_label.config(text=f"X Diff: {current_measurement_data['Signal_xdiff']:.2f}")
    ydiff_label.config(text=f"Y Diff: {current_measurement_data['Signal_ydiff']:.2f}")
    sum_label.config(text=f"Sum: {current_measurement_data['Signal_sum']:.2f}")

    # Plot the x pos and y pos in sensor_plot_frame
    sensor_plot_frame = sensor_info_frame.nametowidget("sensor_plot_frame")
    canvas = sensor_plot_frame.canvas 
    ax = canvas.figure.axes[0]
    #ax.clear() #TODO better updating


    # Initialize the plot if it hasn't been initialized yet
    if not hasattr(tab, 'current_point'):
        tab.current_point, = ax.plot([], [], 'o', color='red')
    else:
        # Plot the current point in red
        current_x = current_measurement_data['Signal_xpos']
        current_y = current_measurement_data['Signal_ypos']
        tab.current_point.set_data([current_x], [current_y])


    

    sensor_plot_frame.canvas.draw()

    