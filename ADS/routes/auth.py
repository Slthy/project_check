import os
import random
import bcrypt

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from db import get_db
from auth import Role
from queries import is_valid_email

auth_bp = Blueprint('auth', __name__)


# Map a role ID to its blueprint dashboard endpoint.
def get_dashboard_route(role_id):
    return {
        Role.ADMIN:   'admin.admin_dashboard',
        Role.GS:      'gs.gs_dashboard',
        Role.ADVISOR: 'advisor.advisor_dashboard',
        Role.STUDENT: 'student.student_dashboard',
        Role.ALUMNI:  'alumni.alumni_dashboard',
    }.get(role_id)


# Redirect users to the right landing page.
@auth_bp.route('/')
def index():
    route = get_dashboard_route(session.get('role_id'))
    if route:
        return redirect(url_for(route))
    return redirect(url_for('auth.login'))


# Handle login and session setup.
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return redirect(url_for('auth.login'))

        student_program_code = None
        db = get_db()

        user = db.execute(
            '''
            SELECT user_id, username, role_id, password_hash
            FROM users
            WHERE username = %s
            ''',
            (username,)
        ).fetchone()

        if user:
            stored_password = user['password_hash'] or ''
            normalized_hash = (
                stored_password.decode('utf-8', errors='ignore')
                if isinstance(stored_password, (bytes, bytearray))
                else str(stored_password)
            )

            try:
                password_ok = bcrypt.checkpw(
                    password.encode('utf-8'),
                    normalized_hash.encode('utf-8')
                )
            except Exception:
                password_ok = False

            if not password_ok:
                user = None

        if user and user['role_id'] == Role.STUDENT:
            student = db.execute(
                '''
                SELECT p.program_code
                FROM students s
                JOIN programs p ON p.program_id = s.program_id
                WHERE s.user_id = %s
                ''',
                (user['user_id'],)
            ).fetchone()
            if student and student['program_code']:
                student_program_code = student['program_code']

        if user is None:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))

        session['user_id'] = user['user_id']
        session['username'] = user['username']
        session['role_id'] = user['role_id']
        session.pop('student_program_code', None)
        if student_program_code:
            session['student_program_code'] = student_program_code

        route = get_dashboard_route(user['role_id'])

        if route:
            flash('Login successful.', 'success')
            return redirect(url_for(route))
        flash('Login failed: unknown user role.', 'error')
        return redirect(url_for('auth.login'))

    route = get_dashboard_route(session.get('role_id'))
    if route:
        return redirect(url_for(route))
    return render_template('login.html')


# Register a new student user.
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        first_name = request.form.get('first_name_student', '').strip()
        last_name = request.form.get('last_name_student', '').strip()
        program_code = request.form.get('program_code', '').strip().upper()
        address = request.form.get('address', '').strip() or None
        email = request.form.get('email', '').strip() or None

        if not username or not password or not confirm_password or not first_name or not last_name or not address or not email or not program_code:
            flash('Username, password, confirm password, first name, last name, address, email, and program are required.', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('auth.register'))

        db = get_db()
        try:
            existing_user = db.execute(
                'SELECT user_id FROM users WHERE username = %s',
                (username,)
            ).fetchone()
            if existing_user:
                flash('Username already exists.', 'error')
                return redirect(url_for('auth.register'))

            student_role = db.execute(
                "SELECT role_id FROM roles WHERE role_name = 'student'"
            ).fetchone()
            if student_role is None:
                flash('Student role is not configured.', 'error')
                return redirect(url_for('auth.register'))

            program_row = db.execute(
                'SELECT program_id FROM programs WHERE UPPER(program_code) = %s',
                (program_code,)
            ).fetchone()
            if not program_row:
                flash('Invalid student program selected. Use MS or PHD.', 'error')
                return redirect(url_for('auth.register'))

            hashed_password = bcrypt.hashpw(
                password.encode('utf-8'), bcrypt.gensalt()
            ).decode('utf-8')
            cursor = db.execute(
                '''
                INSERT INTO users (username, password_hash, role_id)
                VALUES (%s, %s, %s)
                ''',
                (username, hashed_password, student_role['role_id'])
            )
            user_id = cursor.lastrowid

            uid = None
            for _ in range(10):
                candidate_uid = f"{random.randint(0, 99999999):08d}"
                existing_uid = db.execute(
                    'SELECT student_id FROM students WHERE uid = %s',
                    (candidate_uid,)
                ).fetchone()
                if not existing_uid:
                    uid = candidate_uid
                    break

            if uid is None:
                db.rollback()
                flash('Could not generate a unique UID. Please try again.', 'error')
                return redirect(url_for('auth.register'))

            db.execute(
                '''INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (user_id, uid, first_name, last_name, address, email, program_row['program_id'])
            )
            db.commit()
        except Exception as e:
            db.rollback()
            if getattr(e, 'args', None) and e.args[0] == 1062:
                if 'uid' in (e.args[1] if len(e.args) > 1 else ''):
                    flash('A student with that UID already exists.', 'error')
                else:
                    flash('Username already exists.', 'error')
            else:
                flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('auth.register'))

        flash('Registration successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    programs = get_db().execute(
        "SELECT program_code, program_name FROM programs WHERE UPPER(program_code) IN ('MS', 'PHD') ORDER BY CASE UPPER(program_code) WHEN 'MS' THEN 1 WHEN 'PHD' THEN 2 ELSE 3 END"
    ).fetchall()

    return render_template('register.html', programs=programs)


# Clear the session and return to login.
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You were logged out successfully.', 'success')
    return redirect(url_for('auth.login'))
