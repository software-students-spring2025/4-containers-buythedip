"""Test configuration for pytest"""

import os
import sys
import pytest
import mongomock
from flask import Flask

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app


@pytest.fixture
def app():
    """Create test Flask app with mock MongoDB"""
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )

    import app

    mock_client = mongomock.MongoClient()
    mock_db = mock_client["containerapp"]

    original_client = getattr(app, "client", None)
    original_db = getattr(app, "db", None)

    app.client = mock_client
    app.db = mock_db

    yield flask_app

    if original_client is not None:
        app.client = original_client
    if original_db is not None:
        app.db = original_db


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()
