"""
Tests for web app
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app


class Tests:
    """Test cases for the web app."""

    @pytest.fixture
    def client(self):
        """Create a Flask test client for testing routes."""
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client

    def test_home_route(self, client):
        """Ensure the home route returns status code 200 and the expected content."""
        response = client.get("/")
        assert (
            response.status_code == 200
        ), f"Expected status code 200, got {response.status_code}"
        assert (
            b"Database Results" in response.data
        ), "Expected 'Database Results' header in response but it wasn't found"

    def test_upload_route_exists(self, client):
        """Check that the upload route exists (i.e. does not return a 404)."""
        response = client.post("/upload")
        assert response.status_code != 404, "Upload route not found (404)"

    def test_static_directory_exists(self):
        """Verify that the static directory exists."""
        dir_path = "static"
        assert os.path.exists(
            dir_path
        ), f"Expected static directory at {dir_path} but it was not found"
