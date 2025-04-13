"""Tests for the web app"""

import os
import re
import json
import base64
import time
import pytest
import mongomock
from datetime import datetime

from app import app, get_definition, clean_name, db


class DummyResponse:
    def __init__(self, status_code, json_data, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self):
        return self._json


def fake_requests_get_success(url, timeout):
    """
    A fake requests.get that simulates a successful response from MW API.
    It uses the word parsed from the URL.
    """
    word = url.split("/")[-1].split("?")[0]
    if word.lower() in {"bean", "beans"}:
        dummy_json = [
            {
                "def": [
                    {
                        "sseq": [
                            [
                                [
                                    "sense",
                                    {
                                        "sn": "1",
                                        "dt": [
                                            [
                                                "text",
                                                "{bc}{sx|fava bean||}. A leguminous plant used as a food ingredient in various cuisines.",
                                            ]
                                        ],
                                    },
                                ]
                            ],
                            [
                                [
                                    "sense",
                                    {
                                        "sn": "2",
                                        "dt": [
                                            [
                                                "text",
                                                "{bc}The seed of various climbing or erect plants of the legume family.",
                                            ]
                                        ],
                                    },
                                ]
                            ],
                        ]
                    }
                ],
                "shortdef": ["fava bean"],
            }
        ]
        dummy_text = json.dumps(dummy_json)
        return DummyResponse(200, dummy_json, text=dummy_text)
    return DummyResponse(200, [], text="")


@pytest.fixture(autouse=True)
def patch_requests_get(monkeypatch):
    monkeypatch.setattr("app.requests.get", fake_requests_get_success)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mongo_mock():
    """Mongomock client for testing."""
    mock_client = mongomock.MongoClient()
    mock_db = mock_client["containerapp"]
    original_db = db
    app.db = mock_db
    yield
    app.db = original_db


def test_clean_name():
    """Ensure that clean_name removes trailing numbers and extra spaces."""
    assert clean_name("Beans 1") == "Beans"
    assert clean_name("Apple 123") == "Apple"
    assert clean_name("Zucchini") == "Zucchini"


def test_get_definition():
    """Tests the different defintions"""
    definition = get_definition("Bean")
    assert "fava bean" in definition
    assert "A leguminous plant used as a food ingredient" in definition
    assert "The seed of various climbing or erect plants" in definition


def test_home_route(client):
    """Test home route displays dummy data"""
    dummy_entry = {
        "timestamp": int(time.time()),
        "formatted_time": datetime.now().strftime("%I:%M %p"),
        "image_data": base64.b64decode(base64.b64encode(b"dummy_image_data")),
        "status": "processed",
        "classifications": [["Bean 1", 0.95]],
    }
    app.db.images.insert_one(dummy_entry)

    response = client.get("/")
    assert response.status_code == 200
    assert b"fava bean" in response.data or b"No definition available" in response.data


def test_upload_route(client):
    """Test that a valid POST to /upload stores the image and returns a JSON response"""
    dummy_data = base64.b64encode(b"dummy").decode("utf-8")
    dummy_image = f"data:image/jpeg;base64,{dummy_data}"
    response = client.post("/upload", json={"image": dummy_image})
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "image_id" in data


def test_upload_missing_image_data(client):
    """Test that if no image data is provided, the endpoint returns an error."""
    response = client.post("/upload", json={})
    assert response.status_code == 400


def test_find_image_route(client):
    """Insert a dummy image into the database."""
    dummy_entry = {
        "timestamp": int(time.time()),
        "formatted_time": datetime.now().strftime("%I:%M %p"),
        "image_data": base64.b64decode(base64.b64encode(b"dummy_image")),
        "status": "processed",
        "classifications": [["Bean", 0.95]],
    }
    result = app.db.images.insert_one(dummy_entry)
    image_id = str(result.inserted_id)
    response = client.get(f"/image/{image_id}")
    assert response.status_code == 200
    assert "image/jpeg" in response.content_type


def test_status_route(client):
    """Test status route"""
    app.db.images.insert_one(
        {
            "timestamp": int(time.time()),
            "formatted_time": datetime.now().strftime("%I:%M %p"),
            "image_data": b"dummy",
            "status": "pending",
            "classifications": [["Bean", 0.95]],
        }
    )
    response = client.get("/status")
    data = response.get_json()
    assert data.get("pending") is True


def test_home_empty_data(client):
    """Ensure home still works without any data"""
    app.db.images.delete_many({})
    response = client.get("/")
    assert response.status_code == 200
    assert b"No processed images" in response.data or b"Take a photo" in response.data
