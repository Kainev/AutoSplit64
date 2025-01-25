# AutoSplit64
#
# Copyright (C) 2025 Kainev
#
# This project is currently not open source and is under active development.
# You may view the code, but it is not licensed for distribution, modification, or use at this time.
#
# For more information see https://github.com/Kainev/AutoSplit64?tab=readme#license

from typing import Union, Tuple, List

import numpy as np
import cv2

ColourBound = Union[Tuple[int, ...], List[int], np.ndarray]

def in_color_range(image: np.ndarray, lower_bound: ColourBound, upper_bound: ColourBound, threshold: float) -> bool:
    """
    Determines if the proportion of pixels within a specified color range exceeds the given threshold.

    Parameters:
        image (np.ndarray): The input image in BGR or other color space.
        lower_bound (tuple or list or np.ndarray): Lower bound for the color range (e.g., (B, G, R)).
        upper_bound (tuple or list or np.ndarray): Upper bound for the color range (e.g., (B, G, R)).
        threshold (float): The proportion threshold (between 0 and 1).

    Returns:
        bool: True if the proportion of pixels within the color range exceeds the threshold, False otherwise.

    Raises:
        ValueError: If inputs are not within expected ranges or types (only if validate=True).
    """
    if not isinstance(image, np.ndarray):
        raise ValueError("Image must be a NumPy ndarray.")
    
    if not (isinstance(lower_bound, (tuple, list, np.ndarray)) and 
            isinstance(upper_bound, (tuple, list, np.ndarray))):
        raise ValueError("Lower and upper bounds must be tuples, lists, or NumPy arrays.")
    
    if image.ndim != 3 or image.shape[2] not in [1, 3, 4]:
        raise ValueError("Image must have 1, 3, or 4 channels.")
    
    if not (0 <= threshold <= 1):
        raise ValueError("Threshold must be between 0 and 1.")
    
    mask = cv2.inRange(image, lower_bound, upper_bound)
    count = np.count_nonzero(mask)
    
    proportion = count / mask.size
    
    return proportion > threshold