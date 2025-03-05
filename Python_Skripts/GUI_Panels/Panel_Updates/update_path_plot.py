def update_path_plot(root, event = None):
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data
    
    subtab_group = tab.nametowidget("subtab_group")
    sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
    path_plot_frame = sensor_path_frame.nametowidget("path_plot_frame")
    canvas = path_plot_frame.canvas
    ax = canvas.figure.axes[0]

    
    
    # Extract the path coordinates from the data
    path = data['3D']['path']
    slice_index = int(tab.measurement_id_var.get()) + 1
    path_x = path[:slice_index, 0] # Extract path up to the current measurement
    path_y = path[:slice_index, 1]
    path_z = path[:slice_index, 2]


    if not hasattr(tab, 'grid_points'):
        X_flat = data['3D']['X'].flatten()
        Y_flat = data['3D']['Y'].flatten()
        Z_flat = data['3D']['Z'].flatten()

        ax.set_xlim(X_flat.min()-0.1, X_flat.max()+0.1)
        ax.set_ylim(Y_flat.min()-0.1, Y_flat.max()+0.1)
        ax.set_zlim(Z_flat.min()-0.1, Z_flat.max()+0.1)

        tab.grid_points = ax.scatter([X_flat], [Y_flat], [Z_flat], color='blue', label='Meshgrid Points',alpha=0.3, s=1)
        #print("Initialized grid points")

    if not hasattr(tab, 'path'):
        tab.path, = ax.plot([], [], [], color='red', label='Path', linewidth = 1)
        ax.legend()
    else:
        tab.path.set_data(path_x, path_y)
        tab.path.set_3d_properties(path_z)

    canvas.draw()
