"""Tests for the web app"""

import io
import base64
import pytest
from flask import Flask


class Tests:
    """Test cases for the web app"""

    def test_home_route(self, client):
        """Test that the home route returns status 200"""
        response = client.get("/")
        assert response.status_code == 200

    def test_upload_route_exists(self, client):
        """Test that the upload route exists (as a POST endpoint)"""

        dummy_data = base64.b64encode(b"dummy").decode("utf-8")
        dummy_image = f"data:image/jpeg;base64,{dummy_data}"

        response = client.post("/upload", json={"image": dummy_image})
        assert response.status_code in [200, 302, 400]

    def test_static_directory_exists(self, app):
        """Test that the static directory exists"""
        assert "static" in app.static_folder
