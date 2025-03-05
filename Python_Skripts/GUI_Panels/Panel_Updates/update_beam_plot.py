import numpy as np
import matplotlib.pyplot as plt

def update_beam_plot(root, event = None):
        tab_name = root.tab_group.select()
        tab = root.tab_group.nametowidget(tab_name)
        data = tab.data

        subtab_group = tab.nametowidget("subtab_group")
        results_frame = subtab_group.nametowidget("results_frame")
        beam_plot_frame = results_frame.nametowidget("beam_plot_frame")

        canvas = beam_plot_frame.canvas
        ax = canvas.figure.axes[0]

        # Update the beam plot
        ax.clear()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Beam Plot')
        grid_size = data['3D']['grid_size']
        ax.set_xlim(-grid_size[0],0)
        ax.set_ylim(-grid_size[1]/2, grid_size[1]/2)
        ax.set_zlim(-grid_size[2]/2, grid_size[2]/2)

        ax.set_box_aspect([grid_size[1], grid_size[1], grid_size[2]])

        # Plot the seethrough planes
        vertical_index = str(root.vertical_slice_index_var.get())
        horizontal_index = str(root.horizontal_slice_index_var.get())

        # Extract coords
        vertical_key = str(int(data['Visualization']['Slices']['vertical'][vertical_index]['measurement_ids'][0])) # first Measurement
        horizontal_key = str(int(data['Visualization']['Slices']['horizontal'][horizontal_index]['measurement_ids'][0]))
        x_coord = data['Measurements'][vertical_key]['Measurement_point'][0]
        y_coord = data['Measurements'][horizontal_key]['Measurement_point'][2]
        # TODO check correct coords

        # Plot the planes
        # Create meshgrid for planes
        y = np.linspace(-grid_size[1] / 2, grid_size[1] / 2, 10)
        z = np.linspace(-grid_size[2] / 2, grid_size[2] / 2, 10)
        Y, Z = np.meshgrid(y, z)

        # Vertical plane at x_coord
        X_vertical = np.full_like(Y, x_coord)
        ax.plot_surface(X_vertical, Y, Z, color='cyan', theta=0.2, edgecolor='none')

        # Horizontal plane at y_coord
        x = np.linspace(-grid_size[0], 0, 10)
        X, Z = np.meshgrid(x, z)
        Y_horizontal = np.full_like(X, y_coord)
        ax.plot_surface(X, Y_horizontal, Z, color='magenta', theta=0.2, edgecolor='none')


        # Plot the beam
        all_beam_points = data['Visualization']['Beam_Models']['Measured_Beam']['beam_points']
        hull_simplices = data['Visualization']['Beam_Models']['Measured_Beam']['hull_simplices']
        if hull_simplices is not None:
                ax.plot_trisurf(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], triangles=hull_simplices, color='cyan', theta=0.5, edgecolor='black', label='Convex Hull')

        # Plot the beam trajectory 
        if data['Alignment']['trajectory'] is not None:
                trj_vec = data['Alignment']['trajectory']
                #now_plot a line from the start to the end
                # scale the vector to the grid size
                grid_size = data['3D']['grid_size'][0]
                trajectory = np.array([trj_vec[0], trj_vec[1], trj_vec[2]]) * (grid_size) # grid_size*1.1
          

                start_point = np.array(data['Alignment']['Center_Search']['Beam_Centers'][0])
                end_point = start_point + trajectory
               
                
                ax.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], [start_point[2], end_point[2]], color='red', label='Trajectory', linewidth=5)


        # draw probe position ?
        
        index = str(root.measurement_slider_var.get())
        current_point = data["Measurements"][index]["Measurement_point"]

        ax.scatter(current_point[0], current_point[1], current_point[2], color='red', label='Measurement Point', s=100, theta = 0.5)

        ax.legend()
        canvas.draw()