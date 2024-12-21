import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

# Example points
points = np.random.rand(30, 3)  # 30 random points in 2D

# Compute the convex hull
hull = ConvexHull(points)

# Plot the points and the convex hull
plt.plot(points[:, 0], points[:, 1], 'o')
for simplex in hull.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'k-')

plt.show()