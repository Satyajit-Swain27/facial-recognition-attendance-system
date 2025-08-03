import cv2
import os
import sys

# Check for correct arguments
if len(sys.argv) < 3:
    print("Usage: python register_face.py <class_name> <student_name>")
    sys.exit(1)

class_name = sys.argv[1].strip()
student_name = sys.argv[2].strip()

# Folder structure: dataset/ClassName/StudentName
folder_path = os.path.join("dataset", class_name, student_name)
os.makedirs(folder_path, exist_ok=True)

cap = cv2.VideoCapture(0)
count = 0

print(f"📷 Starting face registration for {student_name} in class {class_name}")
print("Press ESC or close the camera window to stop.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to capture frame.")
            break

        cv2.imshow("Register Face", frame)

        # Save every 5th frame to avoid redundancy
        if count % 5 == 0:
            img_path = os.path.join(folder_path, f"{student_name}_{count}.jpg")
            cv2.imwrite(img_path, frame)
            print(f"✅ Saved: {img_path}")

        count += 1

        # Exit on ESC key
        if cv2.waitKey(1) == 27:
            break

except KeyboardInterrupt:
    print("❗ Interrupted by user.")

# Cleanup
cap.release()
cv2.destroyAllWindows()
print(f"✔️ Face registration completed for {student_name} in class {class_name}")
