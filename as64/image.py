# TODO: Rename module? Utility class for image related functions

import numpy as np
import cv2


def in_colour_range(image, lower_bound, upper_bound, threshold):
    result = cv2.inRange(image, lower_bound, upper_bound)
    return np.count_nonzero(result) / result.size > threshold

