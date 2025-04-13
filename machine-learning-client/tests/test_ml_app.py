"""
Tests for the ML client app.
"""

import os
import sys
import numpy as np
from tensorflow.keras.models import load_model  # type: ignore
import cv2

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app
from app import mongo_uri


class Tests:
    """Test cases for ML client application."""

    def test_mdb_connect(self):
        """
        Assert if MongoDB is properly configured and connecting.
        """
        assert isinstance(
            mongo_uri, str
        ), f"Expected mongo_uri to be a string. Instead, it is {type(mongo_uri)}"
        assert len(mongo_uri) > 0, "Expected mongo_uri not to be empty"
        assert mongo_uri.startswith(
            "mongodb://"
        ), f"Expected mongo_uri to start with 'mongodb://'. Instead, it is {mongo_uri}"

    def test_dependencies_installed(self):
        """
        Assert dependencies can be imported and are installed.
        """
        assert "numpy" in sys.modules, "numpy is not imported"
        assert "pymongo" in sys.modules, "pymongo is not imported"

        assert callable(load_model), (
            "tensorflow.keras.models.load_model is not callable. "
            "Ensure that TensorFlow and its Keras submodule are correctly installed."
        )

        assert hasattr(
            cv2, "resize"
        ), "cv2 does not have attribute 'resize'. Check that OpenCV is properly installed."

    def test_classlist_file_exists(self):
        """
        Assert that classlist.json exists at the correct path.
        """
        file_path = "classlist.json"
        assert os.path.exists(
            file_path
        ), f"Expected classlist.json file at {file_path} but it was not found"

    def test_model_file_exists(self):
        """
        Assert that model.h5 exists at the correct path.
        """
        file_path = "model.h5"
        assert os.path.exists(
            file_path
        ), f"Expected model.h5 file at {file_path} but it was not found"
    
    def test_classify_image(self):
        """
        Tests the classify_image function with a dummy image
        """
        dummy = np.zeros((100, 100, 3), dtype=np.uint8) * 255
        
        predictions = app.classify_image(dummy)
        
        assert isinstance(predictions, list), "Predictions should be a list"
        assert len(predictions) > 0, "There should be at least one prediction"
        assert isinstance(predictions[0], tuple), "Each individual prediction should be a tuple"
        assert isinstance(predictions[0][0], str), "The class name should be the first element of the prediction"
        assert isinstance(predictions[0][1], float), "The confidence score should be the second element of the prediction"
        
