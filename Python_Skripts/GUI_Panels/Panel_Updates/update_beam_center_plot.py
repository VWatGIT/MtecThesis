# update Beam Center Plot here

def update_beam_center_plot(root, event = None):
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data
    
    subtab_group = tab.nametowidget("subtab_group")
    sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
    path_plot_frame = sensor_path_frame.nametowidget("beam_center_plot_frame")
    canvas = path_plot_frame.canvas
    ax = canvas.figure.axes[0]

    
    # Extract the path coordinates from the data
    path = data['Alignment']['Center_Search']['Path_Points']
    if path != []:
        path_x = path[0, :]
        path_y = path[1, :]
        path_z = path[2, :]

    # Extract the beam center coordinates from the data
    beam_centers = data['Alignment']['Center_Search']['Beam_Centers']
    if beam_centers != []:    
        beam_centers_x = beam_centers[0, :]
        beam_centers_y = beam_centers[1, :]

    # Now Plot the data
    ax.clear()
    ax.plot(path_x, path_y, path_z, label = 'Path')
    ax.scatter(beam_centers_x, beam_centers_y, label = 'Beam Centers', color = 'red')

