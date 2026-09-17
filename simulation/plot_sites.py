import numpy as np
import matplotlib.pyplot as plt

# Generate the vertices
num_vertices = 50
vertices = np.array([
    [1.1, 19.9],-
    [2.8, 30.4],-
    [4.2, 59.6],-
    [7.4, 39.3],-
    [7.9, 31.6],-
    [8.3, 67.6],-
    [13.1, 86.4],-
    [17.3, 10.1],-
    [17.7, 5.2],-
    [21.6, 38.1],-
    [24.7, 42.5],-
    [26.4, 72.0],-
    [26.7, 2.0],-
    [27.0, 36.4],-
    [27.9, 64.7],-
    [33.4, 74.9],-
    [33.8, 26.9],-
    [35.4, 29.4],-
    [36.1, 48.6],-
    [44.6, 60.5],-
    [49.1, 86.8],-
    [49.7, 14.6],-
    [52.6, 16.7],-
    [52.8, 57.4],-
    [56.8, 62.8],-
    [57.2, 80.9],-
    [57.6, 51.2],-
    [61.5, 63.4],-
    [61.7, 59.6],-
    [61.8, 78.4],-
    [64.1, 18.4],-
    [64.5, 63.3],-
    [70.2, 71.9],-
    [72.8, 69.9],-
    [73.8, 29.6],-
    [74.3, 2.8],-
    [75.6, 52.4],-
    [79.6, 18.1],-
    [81.0, 4.5],-
    [82.1, 81.5],-
    [83.4, 21.7],-
    [84.7, 77.8],-
    [85.4, 69.1],-
    [88.1, 37.3],-
    [88.7, 97.4],-
    [89.7, 12.9],-
    [89.9, 73.4],-
    [95.1, 71.4],-
    [97.4, 68.9]-
])
# Extract x and y coordinates
x_coords = vertices[:, 0]
y_coords = vertices[:, 1]

# Create the scatter plot
plt.scatter(x_coords, y_coords, color='blue', marker='o')

# Add labels and title
plt.xlabel('X Coordinates')
plt.ylabel('Y Coordinates')
plt.title('Scatter Plot of Vertices')

# Display the plot
plt.show()
