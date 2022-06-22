# Plugin
import cv2
from as64 import config
from as64.as64 import GameController, GameStatus
from as64.constants import Region
from as64.plugin import Plugin, Definition

# Keras
from keras import backend as K
from keras.models import load_model

# Numpy
import numpy as np


class Model(object):
    def __init__(self, model_path, width, height):
        K.clear_session()
        
        self.model = load_model(model_path)
        self.model._make_predict_function()
        
        self.width = width
        self.height = height
        
        self.prediction = None
        self.probability = None
        
    def valid(self):
        if self.model:
            return True

        return False
    
    def predict(self, image):
        model_output = self.model.predict(image)
        
        self.prediction = np.argmax(model_output)
        self.probability = np.max(model_output)


class StarDefinition(Definition):
    NAME = "Star Analyzer"
    VERSION = "1.0.0"


class Star(Plugin):
    DEFINITION = StarDefinition
    
    def __init__(self):
        super().__init__()
        
        self._model = None
        
    def initialize(self, ev=None):
        print(config.get("model", "path"))
        self._model = Model(config.get("model", "path"), config.get("model", "width"), config.get("model", "height"))
        
    def execute(self, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
        
        star_region = cv2.resize(convert_to_cv2(status.get_region(Region.STAR)), (self._model.width, self._model.height))
        cv2.imwrite("star.png", cv2.resize(status.get_region(Region.STAR), (self._model.width, self._model.height)))
        
        self._model.predict(convert_to_np([star_region]))
        status.prediction = self._model.prediction
        status.probability = self._model.probability
        
        print("Prediction:", status.prediction)
        print("Probability:", status.probability)



from keras.preprocessing.image import img_to_array


def convert_to_np(img):
    np_images = [(img_to_array(image) / 255) for image in img]

    return np.array(np_images)


def convert_to_cv2(img):
    open_cv_image = np.array(img)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()
