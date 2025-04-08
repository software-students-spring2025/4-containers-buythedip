"""Flask app"""  # TODO: update docstring

import os
import time
import cv2
import pymongo
from flask import Flask, render_template, Response, request, redirect, url_for
from pymongo.errors import PyMongoError

app = Flask(__name__)
camera = cv2.VideoCapture(0)
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/containerapp")

try:
    client = pymongo.MongoClient(mongo_uri)
    db = client.get_database()
    client.admin.command("ping")
    print("Connected to MongoDB")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")


def gen_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n"
            )


@app.route("/")
def home():
    entries = ["test1", "test2", "test3"]
    images = "web-app/static"
    captured_images = [img for img in os.listdir(images) if img.startswith("captured_")]
    return render_template(
        "index.html",
        entries=entries,
        captured_images=sorted(captured_images, reverse=True),
    )


@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/capture", methods=["POST"])
def capture():
    success, frame = camera.read()
    if success:
        name = f"captured_{int(time.time())}.jpg"
        filepath = os.path.join("web-app/static", name)
        cv2.imwrite(filepath, frame)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
