import os
import cv2
import face_recognition
import pickle
import sys

# Root dataset directory: dataset/ClassName/StudentName/
DATASET_DIR = "dataset"

# Loop through each class folder
for class_name in os.listdir(DATASET_DIR):
    class_dir = os.path.join(DATASET_DIR, class_name)
    if not os.path.isdir(class_dir):
        continue

    known_encodings = []
    known_names = []

    print(f"📁 Processing class: {class_name}")

    for student_name in os.listdir(class_dir):
        student_dir = os.path.join(class_dir, student_name)
        if not os.path.isdir(student_dir):
            continue

        print(f"  🔍 Processing student: {student_name}")

        for image_name in os.listdir(student_dir):
            image_path = os.path.join(student_dir, image_name)
            image = cv2.imread(image_path)
            if image is None:
                continue

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            boxes = face_recognition.face_locations(rgb, model="hog")
            encodings = face_recognition.face_encodings(rgb, boxes)

            for encoding in encodings:
                known_encodings.append(encoding)
                known_names.append(student_name)

    # Save encodings for this class
    encoding_file = f"encodings_{class_name}.pickle"
    print(f"  💾 Saving encodings to: {encoding_file}")
    with open(encoding_file, "wb") as f:
        pickle.dump({"encodings": known_encodings, "names": known_names}, f)

print("✅ Class-wise encoding complete!")
sys.exit(0)
