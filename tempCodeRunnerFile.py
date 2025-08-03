import cv2
import numpy as np
import face_recognition
import pickle
import time
import logging
import sys
from datetime import datetime
from blink_utils import BlinkDetector
from database import mark_attendance

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AttendanceSystem")

# ---- Accept class_name as command line argument ----
if len(sys.argv) != 2:
    print("Usage: python antispoof_blink.py <class_name>")
    sys.exit(1)

class_name = sys.argv[1]

# ---- Clear attendance log file at start of session ----
with open("attendance_logs.txt", "w") as f:
    f.write(f"Attendance session started for class: {class_name} - {datetime.now()}\n")

# Load known face encodings and names
try:
    with open("encodings.pickle", "rb") as f:
        data = pickle.load(f)
        known_face_encodings = data["encodings"]
        known_face_names = data["names"]
except FileNotFoundError:
    logger.error("Encoded face data not found. Run encoding script first.")
    sys.exit(1)

# Initialize video capture
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    logger.error("Cannot open webcam")
    sys.exit(1)

blink_detector = BlinkDetector(blink_timeout=5, min_blinks_required=1)
attendance_marked = set()

def log_to_file(name, class_name, already=False):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Already marked" if already else "Marked"
    log_line = f"{status}: {name} | Class: {class_name} | Time: {now}"
    with open("attendance_logs.txt", "a") as f:
        f.write(log_line + "\n")

while True:
    ret, frame = video_capture.read()
    if not ret:
        logger.error("Failed to grab frame from camera.")
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.75, fy=0.75)
    rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small, model="hog")

    if not face_locations:
        cv2.putText(frame, "No face detected", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        top = int(top / 0.75)
        right = int(right / 0.75)
        bottom = int(bottom / 0.75)
        left = int(left / 0.75)

        matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX,
                    0.9, (0, 255, 0), 2)

        face_frame = frame[top:bottom, left:right]
        blink_result = blink_detector.detect_blink(face_frame)

        if blink_result is True:
            if name != "Unknown":
                if mark_attendance(name, class_name):
                    logger.info(f"Attendance marked for: {name} in class {class_name}")
                    print(f"Attendance marked for: {name}")
                    log_to_file(name, class_name)
                else:
                    logger.info(f"Already marked today: {name}")
                    print(f"Already marked today: {name}")
                    log_to_file(name, class_name, already=True)

                cv2.putText(frame, "Blink detected - Attendance marked", (10, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "Blink detected but Unknown face", (10, frame.shape[0] - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        elif blink_result is False:
            cv2.putText(frame, "No blink detected - Possible spoof", (10, frame.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Attendance System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()