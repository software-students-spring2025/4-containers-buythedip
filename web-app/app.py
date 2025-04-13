"""
Flask app for Object Recognizer.

This app allows users to capture images using a webcam. A separate ML client
identifies the fruit in the image and reads out the identification, assisting
visually impaired users.
"""

import base64
import os
import time
import pymongo

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
)
from pymongo.errors import PyMongoError

app = Flask(__name__)
# camera = cv2.VideoCapture(0)
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/containerapp")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command("ping")
    print("Connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")

# No longer needed since we are using getUserMedia instead of cv2
# def gen_frames():
#    while True:
#        success, frame = camera.read()
#        if not success:
#            break
#        else:
#            ret, buffer = cv2.imencode(".jpg", frame)
#            frame = buffer.tobytes()
#            yield (
#                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
#            )


@app.route("/")
def home():
    """Render the home page with processed images and captured images."""
    processed_entries = list(db.images.find({"status": "processed"}))

    base_dir = os.path.dirname(os.path.abspath(__file__)) 
    images = os.path.join(base_dir, "static")

    #images = "static"
    captured_images = [img for img in os.listdir(images) if img.startswith("captured_")]
    return render_template(
        "index.html",
        entries=processed_entries,
        captured_images=sorted(captured_images, reverse=True),
    )


# No longer needed since we are using getUserMedia instead of cv2
# @app.route("/video_feed")
# def video_feed():
#    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/upload", methods=["POST"])
def upload():
    """Process uploaded image, store it, and add its record to MongoDB."""
    data = request.get_json()
    # Split the data URL and ignore the header part.
    _header, encoded = data["image"].split(",", 1)
    binary = base64.b64decode(encoded)

    timestamp = int(time.time())
    filename = f"captured_{timestamp}.jpg"
    file_path = os.path.join("static", filename)
    with open(file_path, "wb") as f:
        f.write(binary)

    try:
        image_doc = {
            "filename": filename,
            "timestamp": timestamp,
            "image_data": binary,
            "status": "pending",
        }
        db.images.insert_one(image_doc)
        print(f"Image {filename} stored in MongoDB")
    except PyMongoError as e:
        print(f"Error storing image in MongoDB: {e}")

    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
