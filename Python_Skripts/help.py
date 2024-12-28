from scipy.spatial.transform import Rotation as R
import numpy as np
from Gauss_Beam import Gauss_Beam


alpha = 45
beta = 0

rotation = R.from_euler('zy', [alpha,beta], degrees=True)

trj = (-1, 0, 0)
new_trj = rotation.apply(trj)

print(new_trj)







