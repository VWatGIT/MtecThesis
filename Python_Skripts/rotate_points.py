import numpy as np
from scipy.spatial.transform import Rotation as R

if __name__ == "__main__":

    old_trj = np.array([-0.9727202, -0.09483338, 0.21171216])
    angles = np.array([1.33668208, 0.0949761, 0.2133265 ])

    desired_angles = np.radians(np.array([90, 0, 0]))

    angle_to_rotate = desired_angles - angles

    #new_trj = rotate_points(old_trj, angles)

    rotation = R.from_euler('xyz', angle_to_rotate, degrees=False)
    new_trj = rotation.apply(old_trj)

    print("Old trajectory: ", old_trj)
    print("New trajectory: ", new_trj)
    print("angles: ", np.degrees(angles))