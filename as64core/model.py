from keras import backend as K
from keras.models import load_model
import numpy as np

from .image_utils import convert_to_np


class PredictionInfo(object):
    def __init__(self, prediction, probability):
        self.prediction = prediction
        self.probability = probability


class Model(object):
    def __init__(self, model_path, width, height):
        K.clear_session()
        try:
            self.model = load_model(model_path)
            self.model._make_predict_function()
        except OSError:
            self.model = None

        self.width = width
        self.height = height

    def valid(self):
        if self.model:
            return True
        else:
            return False

    def predict(self, image) -> PredictionInfo:
        np_img = convert_to_np([image])
        model_output = self.model.predict(np_img)
        prediction = np.argmax(model_output)
        probability = np.max(model_output)

        return PredictionInfo(prediction, probability)

