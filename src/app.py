import base64
import os

import cv2
import numpy as np
from flask import Flask, request#, render_template
from flask_socketio import SocketIO, emit, disconnect
from ultralytics import YOLO
from dotenv import load_dotenv
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

socketio = SocketIO(app, cors_allowed_origins="*")

model = YOLO("src/best.pt")  # Update with your model path


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

DRIVER_AWAKE = "awake"
DRIVER_DROWSY = "drowsy"

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
def handle_connect():
    token = request.args.get('token')  # Get the token from the query parameters
    if token:
        payload = verify_token(token)
        if payload:
            # Token is valid, you can access user information from payload
            emit("connect", f'User {payload} connected.')
        else:
            disconnect()  # Disconnect if the token is invalid or expired
    else:
        disconnect()  # Disconnect if no token is provided

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
        if(top_prediction["class"] == DRIVER_AWAKE):
            emit("prediction_result", 1)
        elif(top_prediction["class"] == DRIVER_DROWSY):
            emit("prediction_result", 0)
    else:
        # If no boxes are found, emit an empty response
        emit("prediction_result", -1)
    

def verify_token(token):
    try:
        # Decode the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload  # Return the payload if the token is valid
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Token is invalid

# @app.route("/")
# def index():
#     return render_template("index.html")

if __name__ == "__main__":
    # Production settings
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 3000))
    
    socketio.run(
        app, 
        host=host, 
        port=port, 
        debug=False,  # Crucial: Always False in production
        use_reloader=False
    )