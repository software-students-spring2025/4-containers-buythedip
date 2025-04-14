"""Tests for the web app"""

import io
import base64
import pytest
from flask import Flask
from app import app

class Tests:
    """Test cases for the web app"""

    def test_home_route(self, client):
        """Test that the home route returns status 200"""
        response = client.get("/")
        assert response.status_code == 200

    # def test_upload_redirects_to_home(self, client):
    #     dummy_data = base64.b64encode(b"dummy").decode("utf-8")
    #     dummy_image = f"data:image/jpeg;base64,{dummy_data}"

    #     response = client.post("/upload", json={"image": dummy_image})
    #     assert response.status_code == 302
    #     assert response.headers["Location"] == "/"


    def test_upload_route_exists(self, client):
        """Test that the upload route exists (as a POST endpoint)"""

        dummy_data = base64.b64encode(b"dummy").decode("utf-8")
        dummy_image = f"data:image/jpeg;base64,{dummy_data}"

        response = client.post("/upload", json={"image": dummy_image})
        assert response.status_code in [200, 302, 400]

    def test_static_directory_exists(self, app):
        """Test that the static directory exists"""
        assert "static" in app.static_folder

    def test_upload_missing_image_data(self, client):
        """Test to see if invalid input is caight properly"""
        response = client.post("/upload", json={}) 
        assert response.status_code == 400 or response.status_code == 500 

    def test_uploaded_image_stored_in_mongo(self, client, app):
        """Test to see if the image is stored in mongodb to be identified"""
        dummy_data = base64.b64encode(b"dummy").decode("utf-8")
        dummy_image = f"data:image/jpeg;base64,{dummy_data}"

        client.post("/upload", json={"image": dummy_image})

        from app import db
        result = list(db.images.find().sort("timestamp", -1).limit(1))
        assert result
        assert result[0]["status"] == "pending"
    
    def test_home_handles_empty_data(self, client):
        """Home page still works when there are no images"""
        response = client.get("/")
        assert response.status_code == 200
        assert b"No processed images" in response.data or b"Object Gallery" in response.data

    def test_get_definition_valid_word(self):
        """Checks to see if definitions are being provided"""
        from app import get_definition
        result = get_definition("python")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_definition_invalid_word(self):
        """Checks to see how a random word that does not exist is being handled by the function"""
        from app import get_definition
        result = get_definition("asdfghjklqwerty")
        assert result == "No definition available."













