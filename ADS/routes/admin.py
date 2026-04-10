from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import pymysql
from auth import role_required, Role
from db import get_db
from queries import is_valid_email
import bcrypt

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# Delete all records that must be removed before a student user can be deleted.
def _delete_student_dependent_records(db, student_id):
    form_rows = db.execute(
        'SELECT form1_id FROM form1 WHERE student_id = %s', (student_id,)
    ).fetchall()
    for form in form_rows:
        db.execute('DELETE FROM graduation_applications WHERE form1_id = %s', (form['form1_id'],))
        db.execute('DELETE FROM form1_courses WHERE form1_id = %s', (form['form1_id'],))
    db.execute('DELETE FROM graduation_applications WHERE student_id = %s', (student_id,))
    db.execute('DELETE FROM form1 WHERE student_id = %s', (student_id,))
    db.execute('DELETE FROM student_enrollments WHERE student_id = %s', (student_id,))


# Show the admin home page.
@admin_bp.route('/dashboard')
@role_required(Role.ADMIN)
def admin_dashboard():
    return render_template('admin/admin_dashboard.html')


# Create users across roles.
@admin_bp.route('/create-user', methods=['GET', 'POST'])
@role_required(Role.ADMIN)
def create_user():
    db = get_db()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()

        if not username or not password or not role:
            flash('Username, password, and role are required.', 'error')
            return redirect(url_for('admin.create_user'))

        role_row = db.execute(
            'SELECT role_id FROM roles WHERE role_name = %s', (role,)
        ).fetchone()

        if not role_row:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('admin.create_user'))

        role_id = role_row['role_id']

        try:
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = db.execute(
                'INSERT INTO users (username, password_hash, role_id) VALUES (%s, %s, %s)',
                (username, password_hash, role_id)
            )
            user_id = cursor.lastrowid
            if role == 'student':
                uid = request.form.get('uid', '').strip()
                first_name = request.form.get('first_name_student', '').strip()
                last_name = request.form.get('last_name_student', '').strip()
                program_code = request.form.get('program_code', '').strip().upper()
                address = request.form.get('address', '').strip() or None
                email = request.form.get('email', '').strip() or None

                if not uid or not first_name or not last_name or not address or not email or not program_code:
                    db.rollback()
                    flash('UID, first name, last name, address, email, and program are required for students.', 'error')
                    return redirect(url_for('admin.create_user'))

                if not is_valid_email(email):
                    db.rollback()
                    flash('Please enter a valid email address.', 'error')
                    return redirect(url_for('admin.create_user'))

                program_row = db.execute(
                    'SELECT program_id FROM programs WHERE UPPER(program_code) = %s',
                    (program_code,)
                ).fetchone()
                if not program_row:
                    db.rollback()
                    flash('Invalid student program selected. Use MS or PHD.', 'error')
                    return redirect(url_for('admin.create_user'))

                db.execute(
                    '''INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                    (user_id, uid, first_name, last_name, address, email, program_row['program_id'])
                )
            elif role in ('advisor', 'grad_secretary'):
                first_name = request.form.get('first_name_faculty', '').strip()
                last_name = request.form.get('last_name_faculty', '').strip()

                if not first_name or not last_name:
                    db.rollback()
                    flash('First name and last name are required for faculty.', 'error')
                    return redirect(url_for('admin.create_user'))

                db.execute(
                    'INSERT INTO faculty (user_id, first_name, last_name) VALUES (%s, %s, %s)',
                    (user_id, first_name, last_name)
                )

            db.commit()
            flash(f'User "{username}" was created successfully.', 'success')
            return redirect(url_for('admin.create_user'))

        except pymysql.IntegrityError as e:
            db.rollback()
            if e.args[0] == 1062:
                if 'uid' in (e.args[1] if len(e.args) > 1 else ''):
                    flash('A student with that UID already exists.', 'error')
                else:
                    flash('Username already exists.', 'error')
            else:
                flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(url_for('admin.create_user'))

    programs = db.execute(
        "SELECT program_code, program_name FROM programs WHERE UPPER(program_code) IN ('MS', 'PHD') ORDER BY CASE UPPER(program_code) WHEN 'MS' THEN 1 WHEN 'PHD' THEN 2 ELSE 3 END"
    ).fetchall()
    return render_template('admin/create_user.html', programs=programs)


# Delete a user and related role data.
@admin_bp.route('/delete-user', methods=['GET', 'POST'])
@role_required(Role.ADMIN)
def delete_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if not username:
            flash('Username is required.', 'error')
            return redirect(url_for('admin.delete_user'))

        db = get_db()
        try:
            user = db.execute(
                'SELECT user_id, role_id FROM users WHERE username = %s',
                (username,)
            ).fetchone()

            if not user:
                flash(f'User "{username}" was not found.', 'error')
                return redirect(url_for('admin.delete_user'))

            if user['user_id'] == session.get('user_id'):
                flash('You cannot delete your own active admin account.', 'error')
                return redirect(url_for('admin.delete_user'))

            role = db.execute(
                'SELECT role_name FROM roles WHERE role_id = %s',
                (user['role_id'],)
            ).fetchone()

            if not role:
                flash('Could not determine the user role.', 'error')
                return redirect(url_for('admin.delete_user'))

            # delete student and all dependent records
            if role['role_name'] == 'student':
                student_row = db.execute(
                    'SELECT student_id FROM students WHERE user_id = %s',
                    (user['user_id'],)
                ).fetchone()
                if student_row:
                    _delete_student_dependent_records(db, student_row['student_id'])
                db.execute('DELETE FROM students WHERE user_id = %s', (user['user_id'],))

            # delete faculty and unassign advisees first
            elif role['role_name'] in ('advisor', 'grad_secretary'):
                faculty_row = db.execute(
                    'SELECT faculty_id FROM faculty WHERE user_id = %s',
                    (user['user_id'],)
                ).fetchone()

                if faculty_row:
                    db.execute(
                        'UPDATE students SET faculty_id = NULL WHERE faculty_id = %s',
                        (faculty_row['faculty_id'],)
                    )

                db.execute(
                    'DELETE FROM faculty WHERE user_id = %s',
                    (user['user_id'],)
                )

            # delete admin profile first
            elif role['role_name'] == 'admin':
                db.execute(
                    'DELETE FROM system_administrators WHERE user_id = %s',
                    (user['user_id'],)
                )

            # delete alumni profile first
            elif role['role_name'] == 'alumni':
                student_row = db.execute(
                    'SELECT student_id FROM students WHERE user_id = %s',
                    (user['user_id'],)
                ).fetchone()
                if student_row:
                    _delete_student_dependent_records(db, student_row['student_id'])
                    db.execute('DELETE FROM students WHERE student_id = %s', (student_row['student_id'],))
                db.execute('DELETE FROM alumni WHERE user_id = %s', (user['user_id'],))

            # finally delete base user row
            db.execute(
                'DELETE FROM users WHERE user_id = %s',
                (user['user_id'],)
            )

            db.commit()
            flash(f'User "{username}" was deleted successfully.', 'success')
            return redirect(url_for('admin.delete_user'))

        except pymysql.MySQLError:
            db.rollback()
            flash('Unable to delete user due to a database error.', 'error')
            return redirect(url_for('admin.delete_user'))

    return render_template('admin/delete_user.html')
