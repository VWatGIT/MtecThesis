from data_handling import load_data, save_data
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.spatial import ConvexHull

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

def detect_edge_points(points, sum_values, sum_treshhold = 3):
    beam_points = []
    for i, sum in enumerate(sum_values):
        if sum > sum_treshhold:
            # assume sum>3 is enough for a point to be part of the beam
            beam_points.append(points[i])

    # Use ConvexHull to find the outermost points
    hull = ConvexHull(beam_points) #TODO research ConvexHull documentation
    edge_points = points[hull.vertices]


    return edge_points

def process_slices(slices):
    all_edge_points = []
    all_heatmaps = []
    for key in slices:
        slice = slices[key]

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

        edge_points = detect_edge_points(points, sum_values)
        all_edge_points.append(edge_points)

    all_edge_points = np.vstack(all_edge_points)

    return all_edge_points, all_heatmaps


if __name__ == "__main__":

    file_path = r'C:/Users/Valen/Documents/Git-Repositorys/MtecThesis/Python_Skripts/Experiment_data/01TSPDKtube_good_inversed_slices.h5'
    data = load_data(file_path) 
    slices = data['Slices']
    
    all_edge_points, all_heatmaps = process_slices(slices)


    '''
    # Create the figure and axes
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    plt.subplots_adjust(left=0.1, bottom=0.25)

    # Plot the initial heatmap
    heatmap_plot = ax1.imshow(all_heatmaps[0], cmap='hot', interpolation='nearest')
    ax1.set_title('Heatmap')
    ax1.set_xlabel('X Coordinate')
    ax1.set_ylabel('Y Coordinate')
    fig.colorbar(heatmap_plot, ax=ax1, label='Signal Sum')


    ax2.set_xlim(0, heatmap.shape[1])
    ax2.set_ylim(0, heatmap.shape[0])

    plt.show()
    '''

    # Create a new figure for the 3D plot
    fig_3d = plt.figure()
    ax_3d = fig_3d.add_subplot(111, projection='3d')

    # Plot the edge points in 3D
    ax_3d.scatter(all_edge_points[:, 0], all_edge_points[:, 1], all_edge_points[:, 2], c='red', s=1)
    ax_3d.set_title('3D Edge Points')
    ax_3d.set_xlabel('X Coordinate')
    ax_3d.set_ylabel('Y Coordinate')
    ax_3d.set_zlabel('Z Coordinate')

    grid_size = data['3D']['grid_size'] 

    ax_3d.set_xlim(-grid_size[0],0)
    ax_3d.set_ylim(-grid_size[1]/2, grid_size[1]/2)
    ax_3d.set_zlim(-grid_size[2]/2, grid_size[2]/2)

    plt.show()
    