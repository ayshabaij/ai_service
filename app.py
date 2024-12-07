from flask import Flask, request, jsonify
import face_recognition
import os
import pickle

app = Flask(__name__)

# Directory to store registered employee encodings
ENCODINGS_DIR = "encodings"
os.makedirs(ENCODINGS_DIR, exist_ok=True)

@app.route('/register', methods=['POST'])
def register_employee():
    """Register an employee by saving their face encoding."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = face_recognition.load_image_file(request.files['image'])
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) == 0:
        return jsonify({"error": "No face detected"}), 400

    # Save the face encoding
    name = request.form.get('name')
    if not name:
        return jsonify({"error": "Employee name is required"}), 400

    encoding_path = os.path.join(ENCODINGS_DIR, f"{name}.pkl")
    with open(encoding_path, 'wb') as f:
        pickle.dump(face_encodings[0], f)

    return jsonify({"status": "Employee registered successfully", "name": name})

@app.route('/recognize', methods=['POST'])
def recognize_face():
    """Recognize a face from the uploaded image."""
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = face_recognition.load_image_file(request.files['image'])
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
            return jsonify({"status": "Face recognized", "name": name})

    return jsonify({"status": "Face not recognized"}), 404

if __name__ == '__main__':
    app.run(debug=True)
