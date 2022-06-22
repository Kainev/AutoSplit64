# Plugin
import cv2
from as64 import config
from as64.as64 import GameController, GameStatus
from as64.constants import Region
from as64.plugin import Plugin, Definition

# Keras
from keras import backend as K
from keras.models import load_model
from keras.preprocessing.image import img_to_array

# Numpy
import numpy as np


def _convert_to_np(img):
    np_images = [(img_to_array(image) / 255) for image in img]

    return np.array(np_images)


def _convert_to_cv2(img):
    open_cv_image = np.array(img)
    # Convert RGB to BGR
    return open_cv_image[:, :, ::-1].copy()


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
        self._star_links = config.get("starlinks")
        self._probability_threshold = config.get("thresholds", "probability")
        
    def initialize(self, ev=None):
        print(config.get("model", "path"))
        self._model = Model(config.get("model", "path"), config.get("model", "width"), config.get("model", "height"))
        
    def execute(self, ev):
        status: GameStatus = ev.status
        controller: GameController = ev.controller
        
        if not controller.predict_star_count:
            return
        
        star_region = cv2.resize(_convert_to_cv2(status.get_region(Region.STAR)), (self._model.width, self._model.height))
        # cv2.imwrite("star.png", cv2.resize(status.get_region(Region.STAR), (self._model.width, self._model.height)))
        
        # Store the last prediction
        previous_prediction = status.prediction
        previous_probability = status.probability
        
        # Predict the current frame
        self._model.predict(_convert_to_np([star_region]))
        status.prediction = self._model.prediction
        status.probability = self._model.probability
        
        #
        next_star = status.star_count + 1
        
        # Last 2 predictions must meet the threshold for a star to be confirmed
        star_confirmed = (previous_prediction in self._star_links[str(next_star)] and
                          previous_probability >= self._probability_threshold and
                          status.prediction in self._star_links[str(next_star)] and
                          status.probability >= self._probability_threshold)
        
        if star_confirmed:
            print("Star Found:", next_star)
            self._set_star_count(status, next_star)
            
    def _set_star_count(self, status: GameStatus, star_count):
        status.star_count = star_count
        
        status.fade_out_count = 0
        status.fade_in_count = 0
        status.x_cam_count = 0

