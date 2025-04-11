"""Tests for the web application"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import url_for


class Tests:
    """Test cases for web app."""

    @pytest.fixture
    def client(self):
        """
        Create a Flask test client for testing routes.
        """
        from app import app

        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_home_route(self, client):
        """
        Verify the home route returns a 200 status code and contains expected content.
        """
        response = client.get("/")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}"
        assert (
            b"test1" in response.data
        ), "Expected 'test1' in response but it wasn't found"
        assert (
            b"test2" in response.data
        ), "Expected 'test2' in response but it wasn't found"
        assert (
            b"test3" in response.data
        ), "Expected 'test3' in response but it wasn't found"

    def test_upload_route_exists(self, client):
        """
        Verify the upload route exists.
        """
        response = client.post("/upload")
        assert response.status_code != 404, "Upload route not found (404)"

    def test_static_directory_exists(self):
        """
        Verify the static directory for storing images exists.
        """
        dir_path = "static"
        assert os.path.exists(
            dir_path
        ), f"Expected static directory at {dir_path} but it was not found"
