import matplotlib.pyplot as plt
import numpy as np
import cv2
from tkinter import filedialog
from scipy.spatial import ConvexHull
from matplotlib.widgets import Slider
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from matplotlib.patches import Ellipse
from scipy.interpolate import griddata

from Python_Skripts.Function_Groups.data_handling import load_data, save_data
from Python_Skripts.Function_Groups.trajectory import calculate_beam_trajectory_LR, calculate_angles
from Python_Skripts.Testing_Scripts.rotate_points import get_rotation_matrix, rotate_points




def create_slices(data, orientation='vertical'):
    # Sort Measurment Points by x coordinate 
    # reverse=True because x coordinates are descending <0
    data['Visualization']['Slices'][orientation] = {}
    if orientation == 'vertical':
        coord_index = 0
    if orientation == 'horizontal':
        coord_index = 2

    sorted_measurements = sorted(data["Measurements"].items(), key=lambda item: item[1]["Measurement_point"][coord_index], reverse=True)
    
    last_x = None
    last_measurement_id = 0
    slice_index = 1 # Start with slice 1
    
    current_slice = {}
    current_slice['measurement_ids'] = []
    

    for measurement_id, measurement in sorted_measurements:
        #measurement = data["Measurements"][str(measurement_id)]
        point = measurement["Measurement_point"]
        current_x = point[coord_index] # slice at different x coordinates
        

        if last_x is None:
            last_x = current_x # for first iteration

        if current_x != last_x:
            # Store the current slice
            data['Visualization']['Slices'][orientation][str(slice_index)] = current_slice
            slice_index += 1
            current_slice = {}
            current_slice['measurement_ids'] = []

        current_slice['measurement_ids'].append(measurement_id)
        last_x = current_x
        last_measurement_id = measurement_id

    # Store the last slice
    if current_slice:
        data['Visualization']['Slices'][orientation][str(slice_index)] = current_slice

    return data

def create_theoretical_slice_points(data, center_point):
    # Calculate the theoretical slice points based on the center point and the beam points
    grid_size = data['3D']['grid_size']
    step_size = data['3D']['step_size']

    x = center_point[0]
    num_elements_y = int(grid_size[1] / step_size[1])
    num_elements_z = int(grid_size[2] / step_size[2])
    
    y_min = -grid_size[1] / 2
    y_max = grid_size[1] / 2
    z_min = -grid_size[2] / 2
    z_max = grid_size[2] / 2

    y = np.linspace(y_min, y_max, num_elements_y)
    z = np.linspace(z_min, z_max, num_elements_z)

    # Create a meshgrid for the y and z coordinates
    Y, Z = np.meshgrid(y, z)

    # Create the theoretical slice points
    slice_points = np.zeros((num_elements_y * num_elements_z, 3))
    slice_points[:, 0] = x
    slice_points[:, 1] = Y.flatten()
    slice_points[:, 2] = Z.flatten()

    return slice_points

def get_theoretical_slice_point_sums(slice_points, data):
    slice_sum_values = np.zeros(len(slice_points))
    step_size = data['3D']['step_size']

    for i, point in enumerate(slice_points):
        # find the closes point in the beam points
        closest_point = None
        closest_sum = None
        closest_distance = np.inf
        beam_points = data['Visualization']['Beam_Models']['Measured_Beam']['beam_points']
        sum_values = data['Visualization']['Beam_Models']['Measured_Beam']['beam_sum_values']
        
        for j, beam_point in enumerate(beam_points):
            distance = np.linalg.norm(point - beam_point)
            if distance < closest_distance and distance < step_size[0]: # TODO decide on distance
                closest_distance = distance
                closest_point = beam_point
                closest_sum = sum_values[j]
            else:
                closest_sum = 0

        slice_sum_values[i] = closest_sum
    return slice_sum_values

def create_slices_non_uniform_x(data, beam_model = 'Rotated_Beam'):
    # Works but too few points? 
    
    data['Visualization']['Beam_Models'][beam_model]

    center_points = data['Visualization']['Beam_Models'][beam_model]['center_points']
    points = data['Visualization']['Beam_Models'][beam_model]['beam_points']
    sum_values = data['Visualization']['Beam_Models'][beam_model]['beam_sum_values']
    
    data['Visualization']['Rotated_Slices'] = {}
    for i, center_point in enumerate(center_points):
        og_slice_point_amount = len(data['Slices']['vertical']['1'].keys())
        #slice_points = np.zeros((og_slice_point_amount, len(points[0])))
        #slice_sum_values = np.zeros(og_slice_point_amount)
         
        slice_points = create_theoretical_slice_points(data, center_point)
        slice_sum_values = get_theoretical_slice_point_sums(slice_points, data)

        print(len(slice_points))
        print(len(slice_sum_values))

        '''
        slice_points = []
        slice_sum_values = []
        for j, point in enumerate(points):

            
            threshhold = 0.1
            if np.isclose(point[0], center_point[0], rtol=threshhold): # TODO decide on R_tol
                slice_points.append(point)
                slice_sum_values.append(sum_values[j])
        '''
                
        if len(slice_points) < 3:
            slice_points.extend([points[0], points[1], points[2]])
            slice_sum_values.extend([sum_values[0], sum_values[1], sum_values[2]])

        heatmap, extent = create_heatmap(slice_points, slice_sum_values, data)
        beam_points, beam_sum_values = detect_beam_points(slice_points, slice_sum_values)
        
        beam_points_2D = np.array(beam_points)[:, 1:]  # Remove the first column
        edge_points_2D, hull = select_edge_points(beam_points_2D) 

        distances_to_center = np.linalg.norm(slice_points - center_point, axis=1)

        slice = {
            'points': slice_points,
            'sum_values': slice_sum_values,
            'distances_to_center': distances_to_center,
            'beam_center': center_point,
            'beam_points': beam_points,
            'beam_points_2D': beam_points_2D,
            'beam_sum_values': beam_sum_values,
            'heatmap': heatmap,
            'heatmap_extent': extent,
            'edge_points_2D': edge_points_2D,
            'hull_2D_vertices': hull.vertices,
            'hull_2D_simplices': hull.simplices
        }
    
        data['Visualization']['Rotated_Slices'][f'Slice_{i+1}'] = slice  

def create_heatmap(points, sum_values, data, orientation='vertical'):
    
    # Convert points to numpy array for easier manipulation
    points = np.array(points)
    sum_values = np.array(sum_values)
    
    if len(points > 0):
        if len(points[0] == 3):
            if orientation == 'vertical':
                points = points[:, 1:]
            if orientation == 'horizontal':
                points = points[:, :2]
    
    # Determine the size of the grid
    grid_size = data['3D']['grid_size'] # [x, y, z]
    step_size = data['3D']['step_size'] # [x, y, z]

    if orientation == 'vertical':
        num_elements_y = int(grid_size[2] / step_size[2])
        num_elements_x = int(grid_size[1] / step_size[1])

        x_min = int(-grid_size[1] / 2)
        x_max = int(grid_size[1] / 2)
        y_min = int(-grid_size[2] / 2)
        y_max = int(grid_size[2] / 2)
    if orientation == 'horizontal':
        num_elements_y = int(grid_size[1] / step_size[1])
        num_elements_x = int(grid_size[0] / step_size[0])

        x_min = int(-grid_size[0])
        x_max = int(0)
        y_min = int(-grid_size[1] / 2)
        y_max = int(grid_size[1] / 2)

    x,y = np.meshgrid(np.linspace(x_min, x_max, num_elements_x), np.linspace(y_min, y_max, num_elements_y))
    
    '''
    z = np.zeros_like(x, dtype=float)
    # Assign values to the grid cells based on the nearest points
    for point, value in zip(points, sum_values):
        # Find the nearest grid cell
        xi = int((point[0] - x_min) / step_size[0])
        yi = int((point[1] - y_min) / step_size[1])

        # Ensure the indices are within bounds
        if 0 <= xi < num_elements_x and 0 <= yi < num_elements_y:
            # Ensure value is a scalar
            if np.isscalar(value):
                z[yi, xi] = value
            else:
                z[yi, xi] = value.item()  # Extract the single element from the array
    '''
    # TODO flip y axis of heatmap?
    if len(points) == 0:
        points = np.array([[0, 0]])
        sum_values = np.array([0])
        z = griddata(points, sum_values, (x, y), method='nearest', fill_value=0)
    else: 
        z = griddata(points, sum_values, (x, y), method='nearest', fill_value=0)
    
    heatmap_extent = [x_min, x_max, y_min, y_max]

    heatmap = z
    return heatmap, heatmap_extent

def detect_beam_points(points, sum_values, orientation='vertical'):
    beam_points = []
    beam_sum_values = []
    if orientation == 'vertical':
        max_intensity = max(sum_values)
        edge_intensity = max_intensity * (1/np.e**2)
        # 1/e^2 of the max intensity
        for i, sum in enumerate(sum_values):
            if sum > edge_intensity:
                beam_points.append(points[i])
                beam_sum_values.append(sum)
    if orientation == 'horizontal':
        for point, sum in zip(points, sum_values):
            if sum > 2.5:
                beam_points.append(point)
                beam_sum_values.append(sum)

    return beam_points, beam_sum_values

def select_edge_points(beam_points):
    # Use ConvexHull to find the outermost points
    hull = ConvexHull(beam_points) #TODO research ConvexHull documentation
    edge_points = beam_points[hull.vertices]

    return edge_points, hull

def extract_slice_data(slice, data):
    points = []
    sum_values = []
    # extract the points and sum values from the slice
    measurement_ids = slice["measurement_ids"]
    for id in measurement_ids:
        point = data['Measurements'][id]["Measurement_point"]
        sum = data['Measurements'][id]["Signal_sum"]
        points.append(point)
        sum_values.append(sum)

    return points, sum_values

def find_slice_beam_center(points, sum_values):
    # Find the center of the beam in the slice
    # Weigh the points by their sum values

    # ASSUME The distortion due to non-orthogonal slicing is negligible

    # Convert points and sum_values to numpy arrays if they are not already
    points = np.array(points)
    sum_values = np.array(sum_values)
    exp_weights = sum_values**2  # Square the sum values to emphasize the importance of the points
    # Calculate the weighted sum of the points
    weighted_sum = np.sum(points * exp_weights[:, np.newaxis], axis=0)

    # Calculate the total sum of the sum values
    total_sum = np.sum(exp_weights)

    # Calculate the weighted average (beam center)
    beam_center = weighted_sum / total_sum
    #print(f'Beam center: {beam_center}')

    return beam_center

def analyze_slice_2D(slice, data):

    points, sum_values = extract_slice_data(slice, data)
    heatmap, heatmap_extent = create_heatmap(points, sum_values, data, orientation='vertical')
    
    
    # First find the beam center
    beam_center = find_slice_beam_center(points, sum_values)  
    distances_to_center = np.linalg.norm(points - beam_center, axis=1)
    # Then use the beam center to find the beam points with w(z)
    beam_points, beam_sum_values = detect_beam_points(points, sum_values, orientation='vertical')
    beam_points = np.array(beam_points)
    beam_sum_values = np.array(beam_sum_values)

    slice['points'] = points
    slice['sum_values'] = sum_values
    slice['beam_center'] = beam_center
    slice['distances_to_center'] = distances_to_center
    slice['beam_points'] = beam_points
    slice['beam_sum_values'] = beam_sum_values
    slice['heatmap'] = heatmap
    slice['heatmap_extent'] = heatmap_extent

def process_slices(data):
    data['Visualization'] = {}
    data['Visualization']['Slices'] = {}
    data['Visualization']['Slices']['vertical'] = {}
    data['Visualization']['Slices']['horizontal'] = {}
    create_slices(data, orientation='vertical')
    create_slices(data, orientation='horizontal')

    for key in data['Visualization']['Slices']['horizontal']:
        slice = data['Visualization']['Slices']['horizontal'][key]
        h_points, h_sum_values = extract_slice_data(slice, data)
        h_points, h_sum_values = detect_beam_points(h_points, h_sum_values, orientation='horizontal')
        h_heatmap, h_heatmap_extent = create_heatmap(h_points, h_sum_values, data, orientation='horizontal')
        data['Visualization']['Slices']['horizontal'][key]['points'] = h_points
        data['Visualization']['Slices']['horizontal'][key]['sum_values'] = h_sum_values
        data['Visualization']['Slices']['horizontal'][key]['heatmap'] = h_heatmap
        data['Visualization']['Slices']['horizontal'][key]['heatmap_extent'] = h_heatmap_extent 
    

    slices = data['Visualization']['Slices']['vertical']
    
    all_beam_points = []
    all_beam_sum_values = []
    all_center_points = []
    

    # Sort the keys in ascending order
    sorted_keys = sorted(slices.keys(), key=int)

    for key in sorted_keys:
        slice = slices[key]

        analyze_slice_2D(slice, data)

        beam_sum_values = data['Visualization']['Slices']['vertical'][key]['beam_sum_values']
        beam_center = data['Visualization']['Slices']['vertical'][key]['beam_center']
        beam_points = data['Visualization']['Slices']['vertical'][key]['beam_points']

        all_center_points.append(beam_center)
        all_beam_points.append(beam_points)
        all_beam_sum_values.extend(beam_sum_values)

    all_center_points = np.vstack(all_center_points)
    all_beam_sum_values = np.vstack(all_beam_sum_values)
    all_beam_points = np.vstack(all_beam_points)
    edge_points, hull = select_edge_points(all_beam_points)
    
    data['Visualization']['Beam_Models'] = {}

    data['Visualization']['Beam_Models']['Measured_Beam'] = {
        'beam_points': all_beam_points,
        'beam_sum_values': all_beam_sum_values,
        'center_points': all_center_points,
        'edge_points': edge_points,   
        # 'hull': hull, not saved because not hdf5 compatible
        'hull_vertices': hull.vertices,
        'hull_simplices': hull.simplices,
    }

    # TODO maybe move trajectory and angles to a separate file?
    try:
        trajectory = calculate_beam_trajectory_LR(all_center_points) 
        angles = calculate_angles(trajectory)
        
        data['Visualization']['Beam_Models']['Measured_Beam']['trajectory'] = trajectory
        data['Visualization']['Beam_Models']['Measured_Beam']['angles'] = angles
    except Exception as e:
        print(f"Error calculating trajectory and angles:")    
    # Rotate the beam to align with the x-axis
    try:
        beam = data['Visualization']['Beam_Models']['Measured_Beam']
        beam = rotate_beam(beam)
        data['Visualization']['Beam_Models']['Rotated_Beam'] = beam
    except Exception as e:
        print(f"Error rotating beam")

    return data    

def rotate_beam(beam):
    # pass the beam dictionary
    trj = beam['trajectory']
    target_vector = np.array([-1, 0, 0])
    rotation_matrix = get_rotation_matrix(trj, target_vector)

    # Apply the rotation matrix to the beam points
    rotated_beam = {}
    rotated_beam['beam_points'] = rotate_points(beam['beam_points'], rotation_matrix)
    rotated_beam['beam_sum_values'] = beam['beam_sum_values']
    rotated_beam['center_points'] = rotate_points(beam['center_points'], rotation_matrix)
    rotated_beam['edge_points'] = rotate_points(beam['edge_points'], rotation_matrix)
    rotated_beam['trajectory'] = rotate_points(beam['trajectory'], rotation_matrix)
    rotated_beam['angles'] = calculate_angles(rotated_beam['trajectory'])
    rotated_beam['hull_simplices'] = beam['hull_simplices']
    rotated_beam['hull_vertices'] = beam['hull_vertices']
    rotated_beam['rotation_matrix'] = rotation_matrix

    return rotated_beam

def plot_slice(data):
    
     # Create the figure and axes with a 2x2 grid layout
    fig, ax1 = plt.subplots(figsize=(12, 8))
   
    ax1.set_aspect('equal', 'box')
    
    
    
    # Plot the initial heatmap
    #TODO add ['Slices']['vertical'] in GUI
    #TODO fix vertical heatmap error
    keys = data['Visualization']['Slices']['vertical'].keys()
    first_key = next(iter(keys))

    heatmap = data['Visualization']['Slices']['vertical'][first_key]['heatmap']
    extent = data['Visualization']['Slices']['vertical'][first_key]['heatmap_extent']

    heatmap_plot = ax1.imshow(heatmap,origin = 'lower', extent=extent,cmap='hot', interpolation='nearest')
    colorbar = fig.colorbar(heatmap_plot, ax=ax1, label='Signal Sum')
    
    #ax1.invert_yaxis()  # invert y axis 
    ax1.set_title('Heatmap')
    ax1.set_xlabel('Y Coordinate')
    ax1.set_ylabel('Z Coordinate')
    
   
    # Create a slider for changing the slice
    slices = data['Visualization']['Slices']['vertical']
    min_slice_index = min(int(key) for key in slices.keys())
    max_slice_index = max(int(key) for key in slices.keys())

    ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slice_slider = Slider(ax_slider, 'Slice', min_slice_index, max_slice_index, valinit=0, valstep=1)

    # Update function for the slider
    def update(val):
        try: 
            slices = data['Visualization']['Slices']['vertical']
            slice_index = int(slice_slider.val)
            current_slice = slices[str(slice_index)]

            # Update heatmap
            heatmap_plot.set_data(current_slice['heatmap'])
        
            # plot the ellipse
            edge_points = current_slice['edge_points_2D']
    
            fig.canvas.draw_idle()
        except KeyError:
            pass
    # Connect the slider to the update function
    slice_slider.on_changed(update)

    plt.show()

def plot_beam(data, beam_model='Measured_Beam'):

    # Create a new figure for the 3D plot
    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(111, projection='3d')

    ax_3d.set_title('3D Edge Points')
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')

    grid_size = data['3D']['grid_size'] 
    grid_size[1] += 2
    grid_size[2] += 2
    grid_size[0] += 2

    ax_3d.set_xlim(-grid_size[0],1)
    ax_3d.set_ylim(-grid_size[1]/2, grid_size[1]/2)
    ax_3d.set_zlim(-grid_size[2]/2, grid_size[2]/2)

    ax_3d.set_box_aspect([grid_size[1], grid_size[1], grid_size[2]])

    # Plot Points 
    all_beam_points = data['Visualization']['Beam_Models'][beam_model]['beam_points']
    edge_points = data['Visualization']['Beam_Models'][beam_model]['edge_points']
    center_points = data['Visualization']['Beam_Models'][beam_model]['center_points']
    
    #ax_3d.scatter(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], c='red', s=1, label='Beam Points')
    #ax_3d.scatter(edge_points[:, 0], edge_points[:, 1], edge_points[:, 2], c='green', s=5, label = 'Edge Points')
    ax_3d.scatter(center_points[:, 0], center_points[:, 1], center_points[:, 2], c='blue', s=5, label='Center Points')
    

    # Plot the convex hull
    hull_simplices = data['Visualization']['Beam_Models'][beam_model]['hull_simplices']
    if hull_simplices is not None:
        ax_3d.plot_trisurf(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], triangles=hull_simplices, color='cyan', alpha=0.5, edgecolor='black', label='Convex Hull')

    # Plot the trajectory
    trajectory = data['Visualization']['Beam_Models'][beam_model]['trajectory']

    start_point = center_points[0]
    start_point = np.array([0, start_point[1], start_point[2]]) 


    # Plot the trajectory vector as an arrow
    ax_3d.quiver(start_point[0], start_point[1], start_point[2],
                trajectory[0], trajectory[1], trajectory[2],
                length=3, color='b', label='Trajectory Vector')

    ax_3d.legend()

    plt.show()
    
def plot_horizontal_slice(data):
    slices = data['Visualization']['Slices']['horizontal']

    # Create the figure and axes
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Plot the initial heatmap
    keys = list(slices.keys())
    first_key = keys[0]

    heatmap = slices[first_key]['heatmap']
    extent = slices[first_key]['heatmap_extent']

    heatmap_plot = ax.imshow(heatmap, origin='lower', extent=extent, cmap='hot', interpolation='nearest')
    colorbar = fig.colorbar(heatmap_plot, ax=ax, label='Signal Sum')

    # Set titles and labels
    ax.set_title('Horizontal Slice Heatmap')
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_aspect(aspect=0.1)


    # Create a slider for changing the slice
    min_slice_index = 0
    max_slice_index = len(keys) - 1

    ax_slider = plt.axes([0.1, 0.1, 0.8, 0.03], facecolor='lightgoldenrodyellow')
    slice_slider = Slider(ax_slider, 'Slice', min_slice_index, max_slice_index, valinit=min_slice_index, valstep=1)

    # Update function for the slider
    def update(val):
        slice_index = int(slice_slider.val)
        current_key = keys[slice_index]
        current_slice = slices[current_key]
        # Update heatmap
        heatmap_plot.set_data(current_slice['heatmap'])
        heatmap_plot.set_extent(current_slice['heatmap_extent'])
        ax.set_aspect(aspect=0.1)
        
        value_min = np.min(current_slice['heatmap'])
        value_max = np.max(current_slice['heatmap'])
        print(value_min, value_max)
        
        heatmap_plot.set_clim(value_min, value_max)
        # Redraw the figure
        fig.canvas.draw_idle()

    # Connect the slider to the update function
    slice_slider.on_changed(update)

    plt.show()

if __name__ == "__main__":

    #file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/01TSPDKtube_good_inversed_slices.h5'
    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/simulated_at_angle.h5'
    data = load_data(file_path) 
    
    process_slices(data)
    
    plot_horizontal_slice(data)

    plot_slice(data)
    #plot_slice(data, Slice_type = 'Rotated_Slices')
    plot_beam(data, beam_model='Measured_Beam')
    #plot_beam(data, beam_model='Rotated_Beam')
    print(data['Visualization']['Beam_Models']['Measured_Beam']['trajectory'])
    #print(data['Visualization']['Beam_Models']['Rotated_Beam']['trajectory'])
    
    '''
    folder_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data'
    save_data(folder_path, data, '01TSPDKtube_now_with_visualization.h5')
    # save once to add Visualization to the data
    '''
   