import numpy as np

def update_beam_center_plot(root, event = None):
    tab = root.tab_group.nametowidget(root.tab_group.select())
    data = tab.data
    
    subtab_group = tab.nametowidget("subtab_group")
    sensor_path_frame = subtab_group.nametowidget("sensor_path_frame")
    path_plot_frame = sensor_path_frame.nametowidget("beam_center_plot_frame")
    canvas = path_plot_frame.canvas
    ax = canvas.figure.axes[0]
  
    
    ax.clear()
    # Extract the path coordinates from the data
    path = data['Alignment']['Center_Search']['Path_Points']
    if path != []:
        # scatter the known path points in blue (even futu)
        path = np.array(path)
        points_x = path[:, 0] 
        points_y = path[:, 1]
        points_z = path[:, 2]

        slice_index = tab.current_point_index # +1 
        path_x = path[:slice_index, 0]
        path_y = path[:slice_index, 1]
        path_z = path[:slice_index, 2]
        
        ax.scatter(points_x, points_y, points_z, label = 'Points to measure', color = 'blue')
        ax.plot(path_x, path_y, path_z, color = 'red', label = 'Path done')
    # Extract the beam center coordinates from the data
    beam_centers = data['Alignment']['Center_Search']['Beam_Centers']
    if beam_centers != []:   
        beam_centers = np.array(beam_centers) 
        beam_centers_x = beam_centers[:, 0]
        beam_centers_y = beam_centers[:, 1]
        beam_centers_z = beam_centers[:, 2]
        
        ax.scatter(beam_centers_x, beam_centers_y, beam_centers_z, label = 'Beam Centers', color = 'red', marker = 'x', s=100)
    
    ax.legend()
    canvas.draw()
    
    
    

