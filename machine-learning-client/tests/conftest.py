"""Test configuration for pytest"""

import os
import pytest
import mongomock


@pytest.fixture(autouse=True)
def mongo_mock():
    """Set up a mongomock client and patch the mongo URI"""
    original_uri = os.environ.get("MONGODB_URI")

    os.environ["MONGODB_URI"] = "mongodb://localhost:27017/testdb"

    mongo_patcher = mongomock.patch(servers=["localhost"])
    mongo_patcher.start()

    client = mongomock.MongoClient("mongodb://localhost:27017")
    client.get_database("testdb")

    yield

    if original_uri:
        os.environ["MONGODB_URI"] = original_uri
    else:
        del os.environ["MONGODB_URI"]

    mongo_patcher.stop()
