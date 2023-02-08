import numpy as np


def point_to_line_distance(point, line_start, line_end):
    line_vector = line_end - line_start
    point_vector = point - line_start
    cross_product = np.cross(point_vector, line_vector)
    distance = np.linalg.norm(cross_product) / np.linalg.norm(line_vector)
    return distance


a = (point_to_line_distance(
    np.array([30, 10]), np.array([25, 20]), np.array([50, 50])))

print(a)
