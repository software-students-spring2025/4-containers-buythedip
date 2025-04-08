import os
import pymongo

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/containerapp")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
