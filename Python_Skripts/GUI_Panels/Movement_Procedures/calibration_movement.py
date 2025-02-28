import tkinter as tk
import random
import math

def take_calibration_images(root):
    camera_object = root.camera_object
    camera = root.camera_object.camera
    hexapod = root.hexapod
    calibration_images = root.camera_object.calibration_images

    # TODO set Hexapod rotation velocity to 200mrad/s (maximum)

    calibration_points = create_calibration_points(root)
    for i, point in enumerate(calibration_points):
        rcv = hexapod.move(point, flag="absolute")
        root.log.log_event(rcv)

        image = None

        # TODO improve this this is only a temporary fix                                                                              
        while image is None:
            try:
                image = camera_object.capture_image() # TODO this shouldnt interfere with the update_camera function
            except Exception as e:
                print("failed to capture image")
                image = None
                pass


        calibration_images.append(image)
        root.log.log_event(f"Took calibration image {i+1} of {len(calibration_points)}")

    hexapod.move_to_default_position()

    return calibration_images

def create_calibration_points(root):
    # 27 points total
    hexapod = root.hexapod
    num_points = root.camera_object.num_calibration_images.get()
    #root.log.log_event(f"Creating {num_points} Calibration Positions")

    # these are not the actual travel ranges, they are already smaller than maximum to allow for rotation about multiple axis simultaneusly
    U_max = hexapod.travel_ranges["U"] 
    V_max = hexapod.travel_ranges["V"] 
    W_max = hexapod.travel_ranges["W"] 


    # create enough calibration points
    angles = [(0,0,0)]
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

    root.log.log_event(f"Created {num_points} calibration positions")

    return calibration_points



if __name__ == "__main__":
    from Python_Skripts.Function_Groups.hexapod import Hexapod
    from Python_Skripts.GUI import UserInterface
    root = tk.Tk()
    app = UserInterface(root, test_mode=True)

    calibration_points = create_calibration_points(root)
    print(calibration_points)
    print(len(calibration_points))

    