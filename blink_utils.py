# import cv2
# import dlib
# import numpy as np
# from scipy.spatial import distance
# import time

# class BlinkDetector:
#     def __init__(self, shape_predictor_path=r"C:\Users\satya\Desktop\attendance_system\models\shape_predictor_68_face_landmarks.dat", ear_threshold=0.21, consecutive_frames=2):
#         self.detector = dlib.get_frontal_face_detector()
#         self.predictor = dlib.shape_predictor(shape_predictor_path)

#         # Eye landmark indices
#         self.LEFT_EYE = list(range(36, 42))
#         self.RIGHT_EYE = list(range(42, 48))

#         # Blink detection parameters
#         self.ear_threshold = ear_threshold
#         self.consecutive_frames = consecutive_frames
#         self.frame_counter = 0
#         self.blinked = False
#         self.last_blink_time = 0
#         self.blink_timeout = 3  # seconds

#     def calculate_ear(self, eye):
#         A = distance.euclidean(eye[1], eye[5])
#         B = distance.euclidean(eye[2], eye[4])
#         C = distance.euclidean(eye[0], eye[3])
#         ear = (A + B) / (2.0 * C)
#         return ear

#     def detect_blink(self, frame):
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         faces = self.detector(gray)

#         if not faces:
#             return None  # No face to evaluate blink

#         for face in faces:
#             shape = self.predictor(gray, face)
#             landmarks = np.array([[shape.part(n).x, shape.part(n).y] for n in range(68)])

#             left_eye = landmarks[self.LEFT_EYE]
#             right_eye = landmarks[self.RIGHT_EYE]

#             left_ear = self.calculate_ear(left_eye)
#             right_ear = self.calculate_ear(right_eye)
#             ear = (left_ear + right_ear) / 2.0

#             if ear < self.ear_threshold:
#                 self.frame_counter += 1
#             else:
#                 if self.frame_counter >= self.consecutive_frames:
#                     self.blinked = True
#                     self.last_blink_time = time.time()
#                 self.frame_counter = 0

#         if self.blinked:
#             if time.time() - self.last_blink_time <= self.blink_timeout:
#                 self.blinked = False
#                 return True  # Valid blink detected
#             else:
#                 self.blinked = False
#                 return False  # Timeout expired, assume spoof
#         else:
#             return None  # Still evaluating


import cv2
import time

class BlinkDetector:
    def __init__(self, blink_timeout=5, min_blinks_required=1):
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.blink_timeout = blink_timeout
        self.min_blinks_required = min_blinks_required
        self.blink_count = 0
        self.eye_detected_prev = False
        self.start_time = None

    def reset(self):
        self.blink_count = 0
        self.eye_detected_prev = False
        self.start_time = None

    def detect_blink(self, frame):
        if self.start_time is None:
            self.start_time = time.time()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = self.eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        eye_detected_now = len(eyes) > 0

        # Detect blink transition: eyes open -> eyes closed
        if self.eye_detected_prev and not eye_detected_now:
            self.blink_count += 1

        self.eye_detected_prev = eye_detected_now

        elapsed = time.time() - self.start_time
        if self.blink_count >= self.min_blinks_required:
            self.reset()
            return True
        elif elapsed > self.blink_timeout:
            self.reset()
            return False

        # Still detecting
        return None
