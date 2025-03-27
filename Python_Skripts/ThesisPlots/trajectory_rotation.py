import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import FancyArrowPatch
from mpl_toolkits.mplot3d.proj3d import proj_transform

# Define two 3D vectors
vector1 = np.array([1, 0, 0])
vector2 = np.array([1/np.sqrt(2), 0 , 1/np.sqrt(2)]) 



# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the vectors
ax.quiver(0, 0, 0, vector1[0], vector1[1], vector1[2], color='blue', label='Vector 1')
ax.quiver(0, 0, 0, vector2[0], vector2[1], vector2[2], color='green', label='Vector 2')


# Annotate the angle
ax.text(0.3, 0.1, 0, f'{angle_degrees:.1f}°', color='red', fontsize=12)

# Set plot limits and aspect ratio
ax.set_xlim([-1.5, 1.5])
ax.set_ylim([-1.5, 1.5])
ax.set_zlim([-1.5, 1.5])
ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

# Add grid and labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.grid(True)

# Add legend
ax.legend()

# Show the plot
plt.show()



