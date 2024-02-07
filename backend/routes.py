import cv2
import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, Response
from flask_pymongo import PyMongo
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from models import Overlay, User
from dotenv import load_dotenv
import os


load_dotenv()

api = Blueprint('api', __name__)

SECRET_KEY = os.getenv('SECRET_KEY_JWT') 
ALGORITHM = "HS256"

def generate_access_token(user_id):
    access_token_payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(minutes=30),  # Set expiration time
    }
    return jwt.encode(access_token_payload, SECRET_KEY, algorithm=ALGORITHM)

def authenticate(username, password):
    user = User.objects(username=username).first()
    if user and user.check_password(password):
        return generate_access_token(user.username)
    else:
        return None

# Register a new user
@api.route('/register', methods=['POST'])
def register_user():
    register_data = request.get_json()
    username = register_data.get('username')
    password = register_data.get('password')

    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    existing_user = User.objects(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    user = User(username=username, password_hash=hashed_password)
    user.save()

    access_token = generate_access_token(user.username)
    return jsonify({"message": "User created successfully", "access_token": access_token}), 201

# Authenticate a user and generate a token
@api.route('/login', methods=['POST'])
def login():
    login_data = request.get_json()
    username = login_data.get('username')
    password = login_data.get('password')

    access_token = authenticate(username, password)
    if access_token:
        return jsonify({"message": "Login successful", "access_token": access_token}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@api.route('/overlays', methods=['GET', 'POST'])
def manage_overlays():
    access_token = request.headers.get('Authorization')
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
    except jwt.exceptions.DecodeError:
        return jsonify({"error": "Invalid token"}), 401

    if request.method == 'GET':
        overlays = [overlay.to_dict() for overlay in Overlay.objects(user_id=user_id)]
        return jsonify({"overlays": overlays})
    elif request.method == 'POST':
        new_overlay = request.get_json()
        new_overlay["user_id"] = user_id  # Add user ID for authorization
        overlay = Overlay(**new_overlay)
        overlay.save()
        return jsonify({"message": "Overlay created successfully.", "overlay": overlay.to_dict()})
    

@api.route('/overlays/<overlay_id>', methods=['PUT', 'DELETE'])
def update_or_delete_overlay(overlay_id):
    user_id = authenticate(request.headers.get('Authorization'), None)  # Authenticate user
    if not user_id:
        return jsonify({"error": "Unauthorized access."}), 401

    try:
        overlay = Overlay.objects.get_or_404({"_id": ObjectId(overlay_id), "user_id": user_id})
    except Overlay.DoesNotExist:
        return jsonify({"error": "Overlay not found"}), 404

    if request.method == 'PUT':
        updated_data = request.get_json()
        for key, value in updated_data.items():
            setattr(overlay, key, value)
        overlay.save()
        return jsonify({"message": "Overlay updated successfully.", "overlay": overlay.to_dict()})
    elif request.method == 'DELETE':
        overlay.delete()
        return jsonify({"message": "Overlay deleted successfully."})

@api.route('/video_feed')
def video_feed():
    def gen():
        cap = cv2.VideoCapture("YOUR_RTSP_URL")  # Replace with your RTSP URL from apps like ONVIF
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            overlays = Overlay.objects(user_id=authenticate(request.headers.get('Authorization'), None))  # Retrieve authorized overlays
            for overlay in overlays:
                x, y, w, h, content = (
                    overlay.x,
                    overlay.y,
                    overlay.width,
                    overlay.height,
                    overlay.content,
                )
                cv2.putText(frame, content, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            try:
                frame = cv2.imencode('.jpg', frame)[1].tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                print(f"Error generating frame: {e}")
                break

        cap.release()

    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

