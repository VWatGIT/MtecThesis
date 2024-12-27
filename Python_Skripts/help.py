from scipy.spatial.transform import Rotation as R
import numpy as np

v_all = []

v1 = [0, 0, 1]
v2 = [0, 1, 0]

v_all.append(v1)
v_all.append(v2)
print(v_all)
v_all = np.vstack(v_all)
print(v_all)


alpha = 45
beta = 45



rotation = R.from_euler('xy', [alpha,beta], degrees=True)
v_rot = []      
v_rot.append(rotation.apply(v_all))
v_rot = np.vstack(v_rot)

print(v_rot)