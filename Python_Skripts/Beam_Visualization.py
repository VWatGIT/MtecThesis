from data_handling import load_data, save_data
import matplotlib.pyplot as plt
import numpy as np
import cv2
from tkinter import filedialog
from scipy.spatial import ConvexHull


def create_slices(data):
    # Sort Measurment Points by x coordinate 
    # reverse=True because x coordinates are descending <0
    sorted_measurements = sorted(data["Measurements"].items(), key=lambda item: item[1]["Measurement_point"][0], reverse=True)
    
    last_x = None
    last_measurement_id = 0
    slice_index = 1 # Start with slice 1
    
    current_slice = {}

    for measurement_id, measurement in sorted_measurements:
        #measurement = data["Measurements"][str(measurement_id)]
        point = measurement["Measurement_point"]
        current_x = point[0] # slice at different x coordinates
        

        if last_x is None:
            last_x = current_x # for first iteration

        if current_x != last_x:
            # Store the current slice
            data["Slices"][str(slice_index)] = current_slice
            slice_index += 1
            current_slice = {}

        current_slice[measurement_id] = measurement
        last_x = current_x
        last_measurement_id = measurement_id

    # Store the last slice
    if current_slice:
        data["Slices"][str(slice_index)] = current_slice

    return data

def create_heatmap(points, sum_values):
    
    # Convert points to numpy array for easier manipulation
    points = np.array(points)
    sum_values = np.array(sum_values)

    points = points[:, 1:]  # Remove the first column
    # Determine the size of the grid
    min_x, min_y = np.min(points, axis=0)
    max_x, max_y = np.max(points, axis=0)
    #print(max_x, max_y, min_x, min_y)

    # Shift points to start from zero
    shifted_points = points - [min_x, min_y]

    # Determine the size of the grid
    grid_width = int(max_x - min_x) + 1
    grid_height = int(max_y - min_y) + 1

    # Create grid for plotting
    heatmap = np.zeros((grid_height, grid_width), dtype=np.uint8)

    # Populate the heatmap with the normalized sum values
    for i, point in enumerate(shifted_points):
        x, y = int(point[0]), int(point[1])
        heatmap[y, x] = sum_values[i]

    return heatmap

def detect_beam_points(points, sum_values, sum_treshhold = 3):
    beam_points = []
    for i, sum in enumerate(sum_values):
        if sum > sum_treshhold:
            # assume sum>3 is enough for a point to be part of the beam
            beam_points.append(points[i])

    return beam_points

def select_edge_points(beam_points):
    # Use ConvexHull to find the outermost points
    hull = ConvexHull(beam_points) #TODO research ConvexHull documentation
    edge_points = beam_points[hull.vertices]

    return edge_points, hull

def process_slices(data):
    slices = data['Slices']
    all_beam_points = []
    all_heatmaps = []

    # Sort the keys in ascending order
    sorted_keys = sorted(slices.keys(), key=int)

    for key in sorted_keys:
        #print(key)
        slice = slices[key]
        #print(f'slice {key} with x = {slice[next(iter(slice))]["Measurement_point"][0]}')
        points = []
        sum_values = []

        # extract the points and sum values from the slice
        for measurement_id in slice:
            point = slice[measurement_id]["Measurement_point"]
            sum = slice[measurement_id]["Signal_sum"]
            points.append(point)
            sum_values.append(sum)

        heatmap = create_heatmap(points, sum_values)
        all_heatmaps.append(heatmap)

        beam_points = detect_beam_points(points, sum_values)
        all_beam_points.append(beam_points)

    all_beam_points = np.vstack(all_beam_points)
    edge_points, hull = select_edge_points(all_beam_points)

    all_heatmaps = np.array(all_heatmaps)

    data['Visualization'] = {
        'beam_points': all_beam_points,
        'edge_points': edge_points,   
        # 'hull': hull, not saved because not hdf5 compatible
        'hull_vertices': hull.vertices,
        'hull_simplices': hull.simplices,
        'all_heatmaps' : all_heatmaps,
    }

    return data    



if __name__ == "__main__":

    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/01TSPDKtube_good_inversed_slices.h5'
    data = load_data(file_path) 

    data['Visualization'] = {}
    process_slices(data)
    
    folder_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data'
    save_data(folder_path, data, '01TSPDKtube_now_with_visualization.h5')
    # TODO save once to add Visualization to the data

    # Create the figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Plot the initial heatmap
    heatmap = data['Visualization']['all_heatmaps'][0]

    heatmap_plot = ax1.imshow(heatmap, cmap='hot', interpolation='nearest')
    ax1.set_title('Heatmap')
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    fig.colorbar(heatmap_plot, ax=ax1, label='Signal Sum')


    ax2.set_xlim(0, heatmap.shape[1])
    ax2.set_ylim(0, heatmap.shape[0])

    plt.show()
    

    # Create a new figure for the 3D plot
    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(111, projection='3d')

    ax_3d.set_title('3D Edge Points')
    ax_3d.set_xlabel('X')
    ax_3d.set_ylabel('Y')
    ax_3d.set_zlabel('Z')

    grid_size = data['3D']['grid_size'] 

    ax_3d.set_xlim(-grid_size[0],0)
    ax_3d.set_ylim(-grid_size[1]/2, grid_size[1]/2)
    ax_3d.set_zlim(-grid_size[2]/2, grid_size[2]/2)

    # Plot Points 
    all_beam_points = data['Visualization']['beam_points']
    edge_points = data['Visualization']['edge_points']


    ax_3d.scatter(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], c='red', s=1)
    ax_3d.scatter(edge_points[:, 0], edge_points[:, 1], edge_points[:, 2], c='green', s=5)

    '''
    # Plot the convex hull
    for simplex in hull.simplices:
        print(simplex)
        #ax_3d.plot(all_beam_points[simplex, 0], all_beam_points[simplex, 1], all_beam_points[simplex, 2], 'k-')
        ax_3d.plot_trisurf(all_beam_points[simplex, 0], all_beam_points[simplex, 1], all_beam_points[simplex, 2], color='cyan', alpha=0.3, edgecolor='black')
    '''

    # Plot the convex hull
    hull_simplices = data['Visualization']['hull_simplices']
    if hull_simplices is not None:
        ax_3d.plot_trisurf(all_beam_points[:, 0], all_beam_points[:, 1], all_beam_points[:, 2], triangles=hull_simplices, color='cyan', alpha=0.5, edgecolor='red')


    plt.show()
    