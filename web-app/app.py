"""
Flask app for Object Recognizer

This app allows users to capture images using a webcam. A separate ML client
identifies the fruit in the image and reads out the identification, assisting
visually impaired users or kids who are in the process of learning which fruits are what.
"""

import base64
import os
import time
import re
from datetime import datetime
import pymongo
import requests
from dotenv import load_dotenv

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    url_for,
    redirect,
    Response,
    make_response,
)
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGODB_URI")
try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command("ping")
    print("Connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")


def clean_name(name):
    """Extract the first word from the classification name and clean it."""
    name = re.sub(r"\s*\d+\s*$", "", name)
    first_word = name.strip().split()[0]
    return first_word


def extract_complete_definition(entry):
    """
    Traverse the 'def' field in the MW API response entry and extract a complete definition.
    Handles cases where item[1] can be either a string or a list.
    """
    defs = entry.get("def", [])

    for sense in defs:
        sseq = sense.get("sseq", [])

        for group in sseq:
            for sense_entry in group:
                if not (isinstance(sense_entry, list) and len(sense_entry) >= 2):
                    continue

                dt = sense_entry[1].get("dt", [])
                parts = []

                for item in dt:
                    if not (isinstance(item, list) and len(item) >= 2):
                        continue

                    content = item[1]
                    if isinstance(content, str):
                        parts.append(content)
                    elif isinstance(content, list):
                        for sub in content:
                            if isinstance(sub, dict) and "t" in sub:
                                parts.append(sub["t"])

                if not parts:
                    continue

                text = " ".join(parts)
                text = re.sub(r"\{[^}]+\}", "", text).strip()
                sentences = re.split(r"\.\s*", text)
                sentences = [s for s in sentences if s.strip()]

                if len(sentences) >= 2:
                    return sentences[1].strip() + "."
                elif sentences:
                    return sentences[0].strip() + "."

    return "No definition available."


def get_definition(word):
    """
    Get a complete definition for the given word using Merriam-Webster's Collegiate Dictionary API.
    Returns a descriptive sentence (complete definition) rather than the abbreviated 'shortdef'.
    """
    api_key = os.environ.get("MW_API_KEY")
    mw_url = os.environ.get(
        "MW_URL", "https://dictionaryapi.com/api/v3/references/collegiate/json"
    )
    url = f"{mw_url}/{word}?key={api_key}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data and isinstance(data[0], dict):
                comp_def = extract_complete_definition(data[0])
                if comp_def:
                    return comp_def
        return "No definition available."
    except Exception as e:
        print(f"Error fetching definition for {word}: {e}")
        return "No definition available."


@app.template_filter("timestamp_to_datetime")
def timestamp_to_datetime(timestamp):
    """Convert Unix timestamp to formatted date string."""
    return datetime.fromtimestamp(timestamp).strftime("%I:%M %p, %b %d")


@app.route("/")
def home():
    """Render home page with processed images and update their definitions in DB."""
    processed_entries = list(
        db.images.find({"status": "processed"}).sort("processed_at", -1)
    )

    for entry in processed_entries:
        classifications = entry.get("classifications", [])

        if not classifications:
            entry["top_class"] = "Unknown"
            entry["definition"] = "No definition available."
            entry["confidence"] = "0%"
            continue

        top_class = classifications[0][0]
        clean_class = clean_name(top_class)
        entry["top_class"] = clean_class

        definition = get_definition(clean_class)
        entry["definition"] = definition

        db.images.update_one(
            {"_id": entry["_id"]},
            {"$set": {"definition": definition}},
        )
        entry["confidence"] = f"{classifications[0][1] * 100:.2f}%"

    return render_template("index.html", entries=processed_entries)


@app.route("/image/<image_id>")
def find_image(image_id):
    """Find and return an image from MongoDB by its ID."""
    try:
        image_doc = db.images.find_one({"_id": ObjectId(image_id)})
        if image_doc and "image_data" in image_doc:
            return Response(image_doc["image_data"], mimetype="image/jpeg")
        return "Image not found", 404
    except Exception as e:
        print(f"Error serving image: {e}")
        return "Error serving image", 500


@app.route("/status")
def check_status():
    """Check if there are any pending images and return status."""
    pending_count = db.images.count_documents({"status": "pending"})
    return jsonify({"pending": pending_count > 0})


@app.route("/upload", methods=["POST"])
def upload():
    """Process uploaded image and store it in DB."""
    data = request.get_json()
    try:
        _header, encoded = data["image"].split(",", 1)
    except (TypeError, KeyError, ValueError):
        return "Invalid image data", 400

    binary = base64.b64decode(encoded)
    timestamp = int(time.time())
    formatted_time = datetime.fromtimestamp(timestamp).strftime("%I:%M %p")

    try:
        image_doc = {
            "timestamp": timestamp,
            "formatted_time": formatted_time,
            "image_data": binary,
            "status": "pending",
        }
        result = db.images.insert_one(image_doc)
        return jsonify(
            {
                "success": True,
                "message": "Image uploaded successfully and is being processed.",
                "image_id": str(result.inserted_id),
            }
        )
    except pymongo.errors.PyMongoError as e:
        print(f"Error storing image in MongoDB: {e}")
        return jsonify({"success": False, "message": "Database error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
