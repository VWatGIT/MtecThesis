import tkinter as tk
import random
import math

def take_calibration_images(root):
    calibration_images = []
    camera = root.camera_object.camera
    hexapod = root.hexapod

    # TODO set Hexapod rotation velocity to 200mrad/s (maximum)

    calibration_points = create_calibration_points(root)

    return calibration_images

def create_calibration_points(root):
    
    hexapod = root.hexapod
    num_points = root.num_calibration_images

    tol = 2 
    spacing = 3

    U_max = hexapod.travel_ranges["U"] - tol
    V_max = hexapod.travel_ranges["V"] - tol
    W_max = hexapod.travel_ranges["W"] - tol


    # create enough calibration points
    angles = []
    for U in [U_max, -U_max, 0]:
        for V in [V_max, -V_max, 0]:
            for W in [W_max, -W_max, 0]:
                angles.append((U, V, W))

    if len(angles) < num_points:
        num_points = len(angles)

    # select random calibration points 
    angles = random.sample(angles, num_points)

    # sort points a bit for faster movement of Hexapod
    # Sort points based on the nearest-neighbor approach
    sorted_angles = [angles.pop(0)]
    while angles:
        last_point = sorted_angles[-1]
        next_point = min(angles, key=lambda x: math.sqrt((x[0] - last_point[0])**2 + (x[1] - last_point[1])**2 + (x[2] - last_point[2])**2))
        sorted_angles.append(next_point)
        angles.remove(next_point)

    # angles.sort(key=lambda x: math.sqrt(x[0]**2 + x[1]**2 + x[2]**2))

    # convert angles to a position for the hexapod
    calibration_points = [(0, 0, 0, x[0], x[1], x[2]) for x in sorted_angles]

    return calibration_points



if __name__ == "__main__":
    from Function_Groups.object3D import Hexapod
    root = tk.Tk()
    root.hexapod = Hexapod()
    root.num_calibration_images = 1000

    calibration_points = create_calibration_points(root)
    print(calibration_points)
    print(len(calibration_points))

    