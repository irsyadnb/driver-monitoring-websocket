import base64

import cv2
import numpy as np
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from ultralytics import YOLO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app)

model = YOLO("src/best.pt")  # Update with your model path

def base64_to_image(base64_string):
    # Extract the base64 encoded binary data from the input string
    base64_data = base64_string.split(",")[1]
    # Decode the base64 data to bytes
    image_bytes = base64.b64decode(base64_data)
    # Convert the bytes to numpy array
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    # Decode the numpy array as an image using OpenCV
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

@socketio.on("connect")
def test_connect():
    print("Connected")
    emit("my response", {"data": "Connected"})

@socketio.on("image")
def receive_image(image):
    # Decode the base64-encoded image data
    image = base64_to_image(image)

    results = model(image)

    # Extract the boxes and sort by confidence
    boxes = results[0].boxes
    if boxes:
        # Find the box with the highest confidence
        top_box = max(boxes, key=lambda box: box.conf.item())

        # Prepare the top prediction
        top_prediction = {
            "class": results[0].names[int(top_box.cls.item())],  # Class name
            "confidence": round(top_box.conf.item(), 2),  # Confidence score
        }

        # Emit the top prediction to the client
        emit("prediction_result", top_prediction)
    else:
        # If no boxes are found, emit an empty response
        emit("prediction_result", {"message": "No detections"})

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
  socketio.run(app, debug=True, port=8000, host='0.0.0.0')