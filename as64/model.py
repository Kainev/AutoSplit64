from keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
import cv2
import numpy as np


model = load_model('resources/model/default_model.hdf5')


img = cv2.imread('1.png')
# img = cv2.resize(img, [67, 40])
# np_image = np.array(img_to_array(img) / 255)

# print(np_image.shape)


cv2.imshow('img', img)
cv2.waitKey(0)
def convert_to_cv2(_img):
    open_cv_image = np.array(_img)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()

model_output = model.predict(cv2.resize(convert_to_cv2(img), (67, 40)))

