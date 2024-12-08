from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import face_recognition
import os
import pickle
import json
import base64
from datetime import datetime
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Enable CORS for all origins (for local testing)
CORS(app, resources={r"/*": {"origins": "*"}})

# Directory to store registered employee encodings
ENCODINGS_DIR = "encodings"
ATTENDANCE_FILE = "attendance.json"

os.makedirs(ENCODINGS_DIR, exist_ok=True)

# Initialize attendance file if not already present
if not os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump({}, f)

# Route for face recognition (main page)
@app.route('/')
def face_recognition_page():
    """Render the face recognition page for marking attendance."""
    return render_template('face_detection.html')

# Route for registering an employee (creating the face encoding)
@app.route('/register', methods=['GET', 'POST'])
def register_employee():
    """Register an employee by saving their face encoding."""
    if request.method == 'POST':
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image = face_recognition.load_image_file(request.files['image'])
        face_encodings = face_recognition.face_encodings(image)

        if len(face_encodings) == 0:
            return jsonify({"error": "No face detected"}), 400

        name = request.form.get('name')
        if not name:
            return jsonify({"error": "Employee name is required"}), 400

        # Save the face encoding
        encoding_path = os.path.join(ENCODINGS_DIR, f"{name}.pkl")
        with open(encoding_path, 'wb') as f:
            pickle.dump(face_encodings[0], f)

        return jsonify({"status": "Employee registered successfully", "name": name})

    return render_template('index.html')

# Route for recognizing a face and marking attendance
@app.route('/recognize', methods=['POST'])
def recognize_face():
    """Recognize a face from the uploaded image and log attendance."""
    data = request.get_json()

    # Decode base64 image
    image_data = base64.b64decode(data['image'].split(',')[1])
    image = Image.open(BytesIO(image_data))
    image = face_recognition.load_image_file(BytesIO(image_data))

    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        return jsonify({"error": "No face detected"}), 400

    # Load all registered encodings
    registered_encodings = {}
    for filename in os.listdir(ENCODINGS_DIR):
        if filename.endswith(".pkl"):
            name = filename[:-4]  # Remove .pkl extension
            with open(os.path.join(ENCODINGS_DIR, filename), 'rb') as f:
                registered_encodings[name] = pickle.load(f)

    # Compare the uploaded face with registered encodings
    uploaded_encoding = face_encodings[0]
    for name, encoding in registered_encodings.items():
        match = face_recognition.compare_faces([encoding], uploaded_encoding)
        if match[0]:
            # If face matches, log attendance
            log_attendance(name)
            return jsonify({"status": f"Attendance marked for {name}."})  # Success response

    # If face not recognized, return error message
    return jsonify({"error": "Face not recognized"}), 404

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    """Render the dashboard with attendance data."""
    with open(ATTENDANCE_FILE, 'r') as f:
        attendance_data = json.load(f)

    return render_template('dashboard.html', attendance_data=attendance_data)

# Helper function to log attendance in the attendance file
def log_attendance(employee_name):
    """Log attendance in the JSON file."""
    with open(ATTENDANCE_FILE, 'r') as f:
        attendance_data = json.load(f)

    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if employee_name not in attendance_data:
        attendance_data[employee_name] = []

    attendance_data[employee_name].append(current_time)

    with open(ATTENDANCE_FILE, 'w') as f:
        json.dump(attendance_data, f, indent=4)

if __name__ == '__main__':
    app.run(debug=True)
