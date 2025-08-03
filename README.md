##  Facial Recognition-Based Anti-Spoofing Attendance System 

A smart attendance system using facial recognition and blink detection to prevent spoofing through photos or videos. Built with Python, Flask, OpenCV, Dlib, and SQLite.

---

##  Features

-  Real-time face recognition
-  Blink-based anti-spoofing detection
-  Web-based student enrollment with automatic face capture
-  Attendance marking with one-time-per-day rule
-  Admin and teacher dashboards with class assignment and record download

---

##  Tech Stack / Skills Used

- Python, Flask for backend logic and routing
- HTML/CSS/JS, Bootstrap for frontend
- OpenCV + Dlib for face & eye detection
- face_recognition for identification
- SQLite for database management
- Subprocess, Base64, Logging, File handling for system integration

---
 Folder Structure

project/
├── app.py
├── database.py
├── encode_faces.py
├── antispoof_blink.py
├── templates/
├── static/
├── dataset/ # [Git-ignored]
├── attendance.db # [Git-ignored]
└── README.md



-------------------------------
2) How to Run

1. **Install dependencies**  

   ```bash
   pip install -r requirements.txt
2. **Run the Flask app**

   ```bash
   python app.py
3. **Access on browser**

    Visit: http://localhost:5000

----------------------------------
🙋‍♂️Team Members

Member 1 – Satyajit Swain

Member 2 – Biswaranjan Padhi

Member 3 – K Ayush Kumar

Member 4 – Satyajeet Padhi

----------------------------------

⚠️ **Note**

 -- The dataset/ folder and attendance.db file are excluded from GitHub for privacy and storage reasons.

 -- Make sure to recreate these locally by enrolling students and running the app.


 ----------------------------
 
