# models_loader.py

import dlib
import os

# Define model paths relative to the project root
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

PREDICTOR_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")
RECOGNITION_MODEL_PATH = os.path.join(MODEL_DIR, "dlib_face_recognition_resnet_model_v1.dat")

def load_models():
    # Check if model files exist
    if not os.path.exists(PREDICTOR_PATH) or not os.path.exists(RECOGNITION_MODEL_PATH):
        raise FileNotFoundError("Model files not found in 'models/' directory.")

    print("✅ Loading models from:", MODEL_DIR)

    # Load dlib models
    face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(PREDICTOR_PATH)
    face_encoder = dlib.face_recognition_model_v1(RECOGNITION_MODEL_PATH)

    return face_detector, shape_predictor, face_encoder
