from tf_keras import backend as K
from tf_keras.models import load_model
import numpy as np
import logging

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
        except OSError as e:
            self.model = None
            logging.error(f"Failed to load model from {model_path}: {str(e)}")
        except Exception as e:
            self.model = None
            logging.error(f"Unexpected error loading model from {model_path}: {str(e)}")

        self.width = width
        self.height = height

    def valid(self):
        if self.model:
            return True
        else:
            return False

    def predict(self, image) -> PredictionInfo:
        try:
            np_img = convert_to_np([image])
            model_output = self.model.predict(np_img, verbose=0)
            prediction = np.argmax(model_output)
            probability = np.max(model_output)

            return PredictionInfo(prediction, probability)
        except Exception as e:
            logging.error(f"Prediction failed: {str(e)}")
            return PredictionInfo(0, 0.0)