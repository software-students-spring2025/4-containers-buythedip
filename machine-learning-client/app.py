"""ML client for image classification and analysis"""

import json
import os
import time

import cv2  # pylint: disable=no-member
import numpy as np
import pymongo
from pymongo.errors import PyMongoError
from tensorflow.keras.models import load_model  # type: ignore  # pylint: disable=import-error,no-name-in-module
from tensorflow.keras.preprocessing_image import img_to_array   # type: ignore  # pylint: disable=import-error,no-name-in-module

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/containerapp")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command("ping")
    print("Connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")

with open("classlist.json", "r", encoding="utf-8") as f:
    CLASS_LIST = json.load(f)

model = load_model("model.h5")  # type: ignore  # pylint: disable=import-error,no-name-in-module

def classify_image(image, top_k=5):
    """Processes an image through the model into k predictions."""

    image = cv2.resize(image, (100, 100))   # pylint: disable=no-member
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # pylint: disable=no-member
    image = img_to_array(image)
    image = image.astype("float32") / 255.0
    image = np.expand_dims(image, axis=0)  # Add batch dimension

    predictions = model.predict(image)[0]
    top_indices = predictions.argsort()[-top_k:][::-1]
    top_predictions = [(CLASS_LIST[i], float(predictions[i])) for i in top_indices]

    return top_predictions


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
                            "classifications": result,
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
    