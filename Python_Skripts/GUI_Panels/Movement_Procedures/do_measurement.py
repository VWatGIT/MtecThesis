def doMeasurement(root, data, sensor, hexapod, i):
    tab = root.tab_group.nametowidget(root.tab_group.select())
   
    # Get the current (theoretical) measurement point
    measurement_point = tab.path_points[i]

    # Get the absolute Hexapod position for the measurement point 
    hexapod_position = hexapod.position

    # Get data from the sensor
    
    if root.simulate_var.get() == 1:
        # create fake random signal
        signal = sensor.get_test_signal()

        intensity = root.gauss_beam.get_Intensity(point = measurement_point)
        # simulate only intensity
        signal.sum = intensity
    else:
        signal = sensor.get_signal()

    measurement_id_str = str(i+1)  # Convert measurement_id to string
    data["Measurements"][measurement_id_str] = {
        
        'Signal_xpos': signal.xpos,
        'Signal_ypos': signal.ypos,
        'Signal_xdiff': signal.xdiff,
        'Signal_ydiff': signal.ydiff,
        'Signal_sum': signal.sum,

        'Measurement_point': measurement_point,
        'Hexapod_position': hexapod_position
    }