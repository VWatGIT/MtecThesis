from pylablib.devices import Thorlabs
import numpy as np
import matplotlib.pyplot as plt

#print(Thorlabs.list_kinesis_devices())

stage = Thorlabs.KinesisQuadDetector("69251980") # 69251980 is the serial number of the Cube KPA101

stage.open()

signal = stage.get_readings()
#info = stage.get_full_info()


# Access the different parameters
xdiff = signal.xdiff
ydiff = signal.ydiff
sum_signal = signal.sum
xpos = signal.xpos
ypos = signal.ypos



print(f"Xdiff: {xdiff}")
print(f"Ydiff: {ydiff}")
#print(info)

stage.close()


# Visualize the signal

# Visualize the signal
plt.figure(figsize=(8, 8))
plt.scatter(xpos, ypos, c='blue', marker='o', label='Signal Position')
plt.axvline(x=xdiff, color='red', linestyle='--', label='X Diff')
plt.axhline(y=ydiff, color='green', linestyle='--', label='Y Diff')
plt.title('Sensor Output')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.legend()
plt.grid(True)
plt.show()


