import numpy as np
import cv2


def colour_percentage(image, lower_bound, upper_bound):
    result = cv2.inRange(image, lower_bound, upper_bound)
    print(result.size)
    print(np.count_nonzero(result))
    return np.count_nonzero(result) / result.size

def show_mask(image, lower_bound, upper_bound):
    mask = cv2.inRange(image, lower_bound, upper_bound)
    output = cv2.bitwise_and(image, image, mask=mask)
    
    cv2.imshow('Mask', output)
    cv2.waitKey(0)


for i in range (14, 20):
    print("IMAGE {} --------------".format(i))
    image = cv2.imread('final_{}.png'.format(i))

    lower_bound = np.array([200, 200, 200], dtype='uint8')
    upper_bound = np.array([255, 255, 255], dtype='uint8')

    print("Result: {:.2f}%".format(colour_percentage(image, lower_bound, upper_bound)*100))

    show_mask(image, lower_bound, upper_bound)
