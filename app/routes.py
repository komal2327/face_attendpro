import qrcode
import io
import base64
from flask import send_file, Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
import io
import base64
import os
from flask import send_file, Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User
from werkzeug.security import generate_password_hash, check_password_hash

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def home():
    return render_template('login.html')

@app_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        enrollment = request.form.get('enrollment')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        if not enrollment or not password or not confirm_password or not role:
            flash('All fields are required.', 'error')
            return render_template('signup.html')
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')
        existing_user = User.query.filter_by(enrollment=enrollment).first()
        if existing_user:
            flash('User already exists. Please login.', 'error')
            return redirect(url_for('app_routes.login'))
        hashed_password = generate_password_hash(password)
        new_user = User(enrollment=enrollment, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('app_routes.login'))
    return render_template('signup.html')

@app_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        enrollment = request.form.get('enrollment')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(enrollment=enrollment, role=role).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if role == 'student':
                return redirect(url_for('app_routes.student_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('app_routes.teacher_dashboard'))
            elif role == 'admin':
                return redirect(url_for('app_routes.admin_dashboard'))
            else:
                return redirect(url_for('app_routes.login'))
        else:
            flash('Invalid credentials or user does not exist.', 'error')
            return render_template('login.html')
    return render_template('login.html')







    if request.method == 'POST':
        enrollment = request.form.get('enrollment')
        password = request.form.get('password')
        role = request.form.get('role')
        user = User.query.filter_by(enrollment=enrollment, role=role).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            if role == 'student':
                return redirect(url_for('app_routes.student_dashboard'))
            elif role == 'teacher':
                return redirect(url_for('app_routes.teacher_dashboard'))
            else:
                return redirect(url_for('app_routes.login'))
        else:
            flash('Invalid credentials or user does not exist.', 'error')
            return render_template('login.html')
    return render_template('login.html')


@app_routes.route('/student/dashboard')
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('app_routes.login'))
    return render_template('student_dashboard.html')

@app_routes.route('/teacher/dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('app_routes.login'))
    return render_template('teacher_dashboard.html')

@app_routes.route('/admin/dashboard')
def admin_dashboard():
    import os
    if session.get('role') != 'admin':
        return redirect(url_for('app_routes.login'))
    logs_dir = os.path.join('attendance_logs')
    student_logs = []
    teacher_logs = []
    for root, dirs, files in os.walk(logs_dir):
        for file in files:
            if file.endswith('_attendance.txt'):
                log_path = os.path.join(root, file)
                try:
                    with open(log_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'Role: teacher' in content or 'role: teacher' in content:
                            teacher_logs.append(content)
                        else:
                            student_logs.append(content)
                except Exception as e:
                    pass
    return render_template('admin_dashboard.html', student_logs=student_logs, teacher_logs=teacher_logs)

@app_routes.route('/attendance', methods=['GET', 'POST'])
def attendance():
    import os
    if request.method == 'POST':
        face_image = request.files.get('face_image')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        subject = request.form.get('subject')
        date = request.form.get('date')
        teacher = request.form.get('teacher')
        student_id = request.form.get('student_id', 'unknown')
        class_name = request.form.get('class_name', 'default_class')
        # Create folder path: attendance_logs/class_name/subject/date
        folder_path = os.path.join('attendance_logs', class_name, subject, date)
        os.makedirs(folder_path, exist_ok=True)
        # Save log file
        log_file = os.path.join(folder_path, f'{student_id}_attendance.txt')
        with open(log_file, 'w') as f:
            f.write(f'Student ID: {student_id}\n')
            f.write(f'Subject: {subject}\n')
            f.write(f'Date: {date}\n')
            f.write(f'Teacher: {teacher}\n')
            f.write(f'Latitude: {latitude}\n')
        teacher = request.args.get('teacher')
        return render_template('attendance.html', subject=subject, date=date, teacher=teacher)

@app_routes.route('/scan_qr', methods=['GET', 'POST'])
def scan_qr():
    if request.method == 'POST':
        # Here you would decode the QR image and redirect to attendance page with details
        # For demo, just redirect to /attendance
        return redirect(url_for('app_routes.attendance'))
    return render_template('scan_qr.html')

@app_routes.route('/generate_qr', methods=['POST'])
def generate_qr():
    subject = request.form.get('subject')
    date = request.form.get('date')
    teacher_name = request.form.get('teacher_name')
    # Data to encode in QR (could be a URL or JSON string)
    qr_data = f"/attendance?subject={subject}&date={date}&teacher={teacher_name}"
    qr_img = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    qr_code_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('teacher_dashboard.html', qr_code_url=qr_code_url)

    # Data to encode in QR (could be a URL or JSON string)
    qr_data = f"/attendance?subject={subject}&date={date}&teacher={teacher_name}"
    qr_img = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr_img.save(buf, format='PNG')
    buf.seek(0)
    qr_code_url = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('utf-8')
    return render_template('teacher_dashboard.html', qr_code_url=qr_code_url)


    @app_routes.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('app_routes.login'))