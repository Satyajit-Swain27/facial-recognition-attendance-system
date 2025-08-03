from flask import Flask,flash, render_template, request, redirect, url_for, session, send_file,jsonify
import os
import subprocess
import base64
from PIL import Image
from io import BytesIO
from datetime import datetime
import re

from database import (
    init_db, verify_user, add_teacher, add_student,
    get_teachers, assign_class,get_students, delete_teacher, delete_student,
    get_teacher_classes,get_teachers_with_classes, mark_attendance, get_attendance_records
)
import sys
print("Python executable:", sys.executable)

# Global variable to track process
camera_process = None
log_file_path = 'attendance_logs.txt'

app = Flask(__name__)
app.secret_key = 'your_secret_key'
init_db()

@app.route('/')
def index():
    return render_template('login_select.html')

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = verify_user(username, password, role)

        if user and user[3] == role:
            session['user'] = username
            session['username'] = username 
            session['user_id'] = user[0]
            session['role'] = role

            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('teacher_dashboard'))
        else:
            return render_template('login.html', role=role, error="Invalid credentials")

    return render_template('login.html', role=role)

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect('/')
    teachers = get_teachers()
    return render_template('admin_dashboard.html', teachers=teachers)

# New GET routes matching the HTML navigation links
@app.route('/enroll/teacher', methods=['GET'])
def enroll_teacher_page():
    return render_template('enroll_teacher.html')

@app.route('/enroll/student', methods=['GET'])
def enroll_student_page():
    return render_template('enroll_student.html')

@app.route('/assign/class', methods=['GET'])
def assign_class_page():
    teachers = get_teachers()
    return render_template('assign_class.html', teachers=teachers)

# POST routes for form submission
@app.route('/admin/enroll_teacher', methods=['POST'])
def enroll_teacher():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    add_teacher(name, username, password)
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/enroll_student', methods=['POST'])
def enroll_student():
    data = request.get_json()
    name = data.get('name')
    class_name = data.get('class_name')
    images = data.get('images')  # List of base64 strings

    if not name or not class_name or not images or not isinstance(images, list):
        return "Missing required data or image list", 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_path = os.path.join('dataset', class_name, name)
    os.makedirs(folder_path, exist_ok=True)

    for i, image_data in enumerate(images):
        image_data = re.sub('^data:image/.+;base64,', '', image_data)
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            filename = f"{name}_{timestamp}_{i+1}.jpg"
            image.save(os.path.join(folder_path, filename))
        except Exception as e:
            return jsonify({'message': f"Error saving image {i+1}: {str(e)}"}), 500

    # Add to DB
    add_student(name, class_name=class_name)

    # Re-encode dataset
    try:
        result = subprocess.run([os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe'), 'encode_faces.py'], check=True)
        return jsonify({'message': f'{name} enrolled with {len(images)} photos!'})
    except subprocess.CalledProcessError as e:
        return jsonify({'message': f'Encoding failed: {e.stderr}'}), 500


@app.route('/admin/assign_class', methods=['POST'])
def assign_class_route():  
    teacher_username = request.form['teacher_username']
    class_name = request.form['class_name']
    from database import assign_class 
    assign_class(teacher_username, class_name) 
    return redirect(url_for('admin_dashboard'))


@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login', role='teacher'))

    teacher_username = session['username'] 
    classes = get_teacher_classes(teacher_username)

    return render_template('teacher_dashboard.html', classes=classes)



@app.route('/start_attendance', methods=['POST'])
def start_attendance():
    if 'user_id' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login', role='teacher'))

    selected_class = request.form['class_name']
    session['selected_class'] = selected_class

    try:
        # Launch antispoof_blink.py with the selected class name
        
        subprocess.Popen([sys.executable, 'antispoof_blink.py', selected_class])

        flash(f"Camera launched for class: {selected_class}", "info")
    except Exception as e:
        flash(f"Failed to launch attendance system: {e}", "danger")

    return render_template('take_attendance.html', class_name=selected_class)


@app.route('/download_attendance')
def download_attendance():
    import csv
    filename = "attendance.csv"
    records = get_attendance_records()
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Student Name", "Class Name", "Timestamp"])
        writer.writerows(records)
    return send_file(filename, as_attachment=True)

# View Teacher List Page
@app.route('/admin/teacher_list')
def view_teacher_list():
    teachers = get_teachers_with_classes()
    return render_template('teacher_list.html', teachers=teachers)

# View Student List Page
@app.route('/admin/student_list')
def view_student_list():
    students = get_students()
    return render_template('student_list.html', students=students)

# Delete Teacher
@app.route('/admin/delete_teacher/<int:teacher_id>', methods=['POST'])
def delete_teacher_route(teacher_id):
    delete_teacher(teacher_id)
    return redirect(url_for('view_teacher_list'))

# Delete Student
@app.route('/admin/delete_student/<int:student_id>', methods=['POST'])
def delete_student_route(student_id):
    delete_student(student_id)
    return redirect(url_for('view_student_list'))


@app.route('/attendance_logs')
def attendance_logs():
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as f:
            return f.read()
    return "No logs available yet."


@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_process
    if camera_process and camera_process.poll() is None:
        camera_process.terminate()
        camera_process = None
        flash('Camera stopped successfully.', 'success')
    else:
        flash('Camera is not currently running.', 'warning')
    return redirect(url_for('teacher_dashboard'))


@app.route('/admin/download_teachers')
def download_teachers():
    import csv
    from database import get_teachers_with_classes  # Use the enhanced function

    teachers = get_teachers_with_classes()
    filename = "teachers.csv"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Username", "Password", "Assigned Classes"])
        for t in teachers:
            writer.writerow([t["id"], t["username"], t["password"], t["classes"]])

    return send_file(filename, as_attachment=True)


# Download Student CSV
@app.route('/admin/download_students')
def download_students():
    import csv
    students = get_students()
    filename = "students.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Student ID", "Class Name"])
        writer.writerows([(s["name"], s["student_id"], s["class_name"]) for s in students])
    return send_file(filename, as_attachment=True)



@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('index'))  # Or redirect to 'login' if you prefer


if __name__ == '__main__':
    app.run(debug=True)
