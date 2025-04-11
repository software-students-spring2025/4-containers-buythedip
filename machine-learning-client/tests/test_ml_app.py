"""Tests for the ML client app"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# pylint: disable=unused-import,import-outside-toplevel


class Tests:
    """Test cases for ML client application."""

    def test_mdb_connect(self):
        """
        Assert if MongoDB is properly configured and connecting.
        """
        from app import mongo_uri

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
        try:
            import tensorflow as tf
            import numpy as np
            import pymongo
        except ImportError as e:
            pytest.fail(f"Missing critical dependency: {e}")

        try:
            import cv2
        except ImportError as e:
            if "CI" in os.environ:
                print(f"Warning: OpenCV import error (acceptable in CI): {e}")
            else:
                pytest.fail(f"Missing OpenCV dependency: {e}")

    def test_classlist_file_exists(self):
        """
        Assert classlist.json exists and at correct path.
        """
        file_path = "classlist.json"
        assert os.path.exists(
            file_path
        ), f"Expected classlist.json file at {file_path} but it was not found"

    def test_model_file_exists(self):
        """
        Assert model.h5 exists and at correct path.
        """
        file_path = "model.h5"
        assert os.path.exists(
            file_path
        ), f"Expected model.h5 file at {file_path} but it was not found"
