import numpy as np

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
        # scatter the known path points in blue (even futu)
        path = np.array(path)
        points_x = path[:, 0] 
        points_y = path[:, 1]
        points_z = path[:, 2]

        slice_index = tab.current_point_index # +1 
        path_x = path[:slice_index, 0]
        path_y = path[:slice_index, 1]
        path_z = path[:slice_index, 2]
        

        if not hasattr(tab, 'points_to_measure_plot'):
            tab.points_to_measure_plot = ax.scatter(points_x, points_y, points_z, label = 'Points to measure', color = 'blue', alpha = 0.3, s=3)
        else:
            ax.scatter(points_x, points_y, points_z, color = 'blue', alpha = 0.3, s=3)

        if not hasattr(tab, 'center_search_path'):
            tab.center_search_path = ax.plot(path_x, path_y, path_z, label='Path done', color='lightsteelblue', linewidth = 0.5)
        else:
            ax.plot(path_x, path_y, path_z, color='lightsteelblue', linewidth = 0.5)
            #tab.center_search_path.set_data(path_x, path_y)
            #tab.center_search_path.set_3d_properties(path_z)

    # Extract the beam center coordinates from the data
    beam_centers = data['Alignment']['Center_Search']['Beam_Centers']
    if beam_centers != []:   
        beam_centers = np.array(beam_centers) 
        beam_centers_x = beam_centers[:, 0]
        beam_centers_y = beam_centers[:, 1]
        beam_centers_z = beam_centers[:, 2]
        
        if not hasattr(tab, 'beam_centers_plot'):
            tab.beam_centers_plot = ax.scatter(beam_centers_x, beam_centers_y, beam_centers_z, label='Beam Centers', color='red', marker='x', s=200)
        else:
            ax.scatter(beam_centers_x, beam_centers_y, beam_centers_z, color='red', marker='x', s=200)
            #tab.beam_centers_plot._offsets3d = (beam_centers_x, beam_centers_y, beam_centers_z)

    if data['Alignment']['trajectory'] is not None:
        trj = np.array(data['Alignment']['trajectory'])
        
        centers = data['Alignment']['Center_Search']['Beam_Centers']
        centers = np.array(centers)
        
        origin = np.array(centers[0])

        def center_line(trj, origin, t):
            return trj * t  + origin
        
        max_distance = np.sqrt(np.sum((centers[0] - centers[-1])**2)) 

        t_values = np.linspace(-max_distance*0.2,max_distance*1.2, 100)

        trj_x = [center_line(trj, origin, t)[0] for t in t_values]
        trj_y = [center_line(trj, origin, t)[1] for t in t_values]
        trj_z = [center_line(trj, origin, t)[2] for t in t_values]

        ax.plot(trj_x, trj_y, trj_z, label='Beam Trajectory', color='red', linewidth = 2, linestyle='dashed')

    ax.legend()
    canvas.draw()
    
    
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from Python_Skripts.Function_Groups.trajectory import calculate_beam_trajectory_LR

    fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]') 

    centers = np.array([[0, 0, 0], [-1, 0, 0], [-2, 0, 0], [-3, 0, 0]])

    trj = calculate_beam_trajectory_LR(centers)
    print(trj)
    data = {'Alignment': {'Center_Search': {'Beam_Centers': centers}}}
    data['Alignment']['trajectory'] = trj

    
    
    if data['Alignment']['trajectory'] is not None:
        trj = np.array(data['Alignment']['trajectory'])
        
        centers = data['Alignment']['Center_Search']['Beam_Centers']
        origin = np.array(centers[0])

        def center_line(trj, origin, t):
            return trj * t  + origin
        
        max_distance = np.sqrt(np.sum((centers[0] - centers[-1])**2)) 

        t_values = np.linspace(-max_distance*0.25, max_distance*1.25, 100)

        trj_x = [center_line(trj, origin, t)[0] for t in t_values]
        trj_y = [center_line(trj, origin, t)[1] for t in t_values]
        trj_z = [center_line(trj, origin, t)[2] for t in t_values]

        ax.plot(trj_x, trj_y, trj_z, label='Beam Trajectory', color='cyan', linewidth = 2, linestyle='dashed')
        
        for center in centers:
            ax.scatter(center[0], center[1], center[2], label='Beam Centers', color='red', marker='x', s=300)


        plt.show()