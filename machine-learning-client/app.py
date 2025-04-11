"""ML client for image classification and analysis"""

import json
import os
import time

import cv2  # pylint: disable=no-member
import numpy as np
import pymongo
from pymongo.errors import PyMongoError
from tensorflow.keras.models import load_model  # type: ignore  # pylint: disable=import-error,no-name-in-module

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/containerapp")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command("ping")
    print("Connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")

with open("classlist.json", "r", encoding="utf-8") as f:
    class_list = json.load(f)

model = load_model("model.h5")  # type: ignore  # pylint: disable=import-error,no-name-in-module


def classify_image(img):
    """Classify an image using the loaded model."""
    img_resized = cv2.resize(img, (100, 100))  # pylint: disable=no-member
    img_rgb = cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member
    img_batch = np.expand_dims(img_rgb, axis=0)

    prediction = model.predict(img_batch)
    class_idx = np.argmax(prediction[0])
    class_name = class_list[class_idx]
    confidence = float(prediction[0][class_idx])

    return {"class": class_name, "confidence": confidence}


def process_pending_images():
    """Poll database for new images and process them."""
    while True:
        try:
            pending = db.images.find_one({"status": "pending"})

            if pending:
                image_data = pending["image_data"]

                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # pylint: disable=no-member

                result = classify_image(img)

                db.images.update_one(
                    {"_id": pending["_id"]},
                    {
                        "$set": {
                            "status": "processed",
                            "classification": result["class"],
                            "confidence": result["confidence"],
                            "processed_at": int(time.time()),
                        }
                    },
                )
            time.sleep(1)
        except PyMongoError as e:
            print(f"Error processing images: {e}")
            time.sleep(5)


if __name__ == "__main__":
    process_pending_images()
