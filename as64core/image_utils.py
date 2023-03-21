import numpy as np
from keras_preprocessing.image import img_to_array
import cv2


def is_black(image, threshold=0.1, percent_threshold=0.9):
    img_1d = convert_to_np([image]).flatten()
    return np.sum(img_1d < threshold) > len(img_1d) * percent_threshold


def is_white(image, threshold=0.8):
    img_1d = convert_to_np([image]).flatten()
    return np.sum(img_1d > threshold) > len(img_1d) * 0.99


def convert_to_np(img_array):
    np_images = [(img_to_array(image) / 255) for image in img_array]

    return np.array(np_images)


def convert_to_cv2(img):
    open_cv_image = np.array(img)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()


def cv2_convert_to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def np_convert_to_gray(np_rgb):
    return np.dot(np_rgb[..., :3], [0.299, 0.587, 0.114])
