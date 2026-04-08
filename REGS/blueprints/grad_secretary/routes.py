"""
Graduate secretary routes: student records, transcripts, course schedule, and grade overrides.

All routes require an authenticated session with role 'grad_secretary' or
'system_admin'. Routes are registered on the 'grad_secretary' blueprint.
"""

from flask import render_template, request, flash, redirect, url_for, current_app, session
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import grad_secretary
import pymysql

from flask_babel import _

@grad_secretary.route('/')
@login_required
@role_required('system_admin', 'grad_secretary')
def index():
    return redirect(url_for('grad_secretary.records'))

@grad_secretary.route('/records')
@login_required
@role_required('system_admin', 'grad_secretary')
def records():
    students = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.id, CONCAT(u.fname, " ", u.lname) AS name,
                   u.email, st.track, st.admit_year
            FROM users u
            JOIN stud_type st ON u.id = st.id
            WHERE u.role = 3
            ORDER BY u.lname
        ''')
        students = cursor.fetchall()
        current_app.logger.info(f"Grad Secretary {gs_id} accessed the global student records list.")
    except pymysql.Error as e:
        flash(_("Error loading student records."), "error")
        current_app.logger.error(f"DB error in gs records: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('grad_secretary/gs_records.html', students=students)


@grad_secretary.route('/records/<int:uid>')
@login_required
@role_required('system_admin', 'grad_secretary')
def student_transcript(uid):
    student = None
    courses = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT fname, lname, email FROM users WHERE id = %s', (uid,))
        student = cursor.fetchone()
        cursor.execute('''
            SELECT c.dept, c.number, c.name, c.credits,
                   e.grade, o.semester, o.year
            FROM enrollment e
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN plan p ON e.plan_id = p.plan_id
            WHERE p.owner_id = %s
            ORDER BY o.year, o.semester
        ''', (uid,))
        courses = cursor.fetchall()
        current_app.logger.info(f"Grad Secretary {gs_id} accessed the transcript for student ID {uid}.")
    except pymysql.Error as e:
        flash(_("Error loading transcript."), "error")
        current_app.logger.error(f"DB error in gs transcript: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('grad_secretary/gs_transcript.html', student=student, courses=courses)


@grad_secretary.route('/schedule')
@login_required
@role_required('system_admin', 'grad_secretary')
def schedule():
    courses = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.dept, c.number, c.name, c.credits,
                   o.semester, o.year, s.day, s.start_time, s.end_time,
                   CONCAT(u.fname, " ", u.lname) AS instructor
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            LEFT JOIN users u ON o.i_id = u.id
            ORDER BY s.day, s.start_time
        ''')
        courses = cursor.fetchall()
        current_app.logger.info(f"Grad Secretary {gs_id} accessed the full course schedule.")
    except pymysql.Error as e:
        flash(_("Error loading schedule."), "error")
        current_app.logger.error(f"DB error in gs schedule: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('grad_secretary/gs_schedule.html', courses=courses)


@grad_secretary.route('/override-grades')
@login_required
@role_required('system_admin', 'grad_secretary')
def override_grades():
    enrollments = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.enroll_id, CONCAT(u.fname, " ", u.lname) AS student_name,
                   c.dept, c.number, c.name, e.grade
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            ORDER BY u.lname, c.dept, c.number
        ''')
        enrollments = cursor.fetchall()
        current_app.logger.info(f"Grad Secretary {gs_id} accessed the grade override master list.")
    except pymysql.Error as e:
        flash(_("Error loading grades."), "error")
        current_app.logger.error(f"DB error in gs override grades: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('grad_secretary/gs_override_grades.html', enrollments=enrollments)


@grad_secretary.route('/override-grades/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'grad_secretary')
def submit_override(enroll_id):
    grade = request.form.get('grade')
    gs_id = session.get('user_id', 'Unknown')
    valid_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP'}

    if grade not in valid_grades:
        flash(_("Invalid grade selected."), "error")
        current_app.logger.warning(f"Grad Secretary {gs_id} attempted an invalid grade override ('{grade}') for enrollment {enroll_id}.")
        return redirect(url_for('grad_secretary.override_grades'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE enrollment SET grade = %s WHERE enroll_id = %s',
            (grade, enroll_id)
        )
        conn.commit()
        flash(_("Grade updated successfully."), "success")
        current_app.logger.info(f"Grad Secretary {gs_id} successfully overrode grade to '{grade}' for enrollment {enroll_id}.")
    except pymysql.Error as e:
        flash(_("A database error occurred."), "error")
        current_app.logger.error(f"DB error in gs submit_override: {e}")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('grad_secretary.override_grades'))

@grad_secretary.route('/schedule/add', methods=['POST'])
@login_required
@role_required('system_admin', 'grad_secretary')
def add_offering():
    gs_id = session.get('user_id', 'Unknown')
    conn = None
    try:
        dept = request.form.get('dept').strip().upper()
        number = request.form.get('number').strip()
        semester = request.form.get('semester')
        year = request.form.get('year')
        day = request.form.get('day')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        conn = get_db_connection()
        cursor = conn.cursor()

        name = request.form.get('name', '').strip()
        credits = request.form.get('credits', 3)

        cursor.execute(
            'SELECT c_id FROM c_catalog WHERE dept = %s AND number = %s',
            (dept, number)
        )
        course = cursor.fetchone()

        if not course:
            cursor.execute('''
                INSERT INTO c_catalog (dept, number, name, credits)
                VALUES (%s, %s, %s, %s)
            ''', (dept, number, name, credits))
            conn.commit()
            c_id = cursor.lastrowid
        else:
            c_id = course['c_id']

        cursor.execute('''
            INSERT INTO c_offering (c_id, semester, year, section)
            VALUES (%s, %s, %s, 1)
        ''', (c_id, semester, year))
        conn.commit()

        o_id = cursor.lastrowid

        cursor.execute('''
            INSERT INTO schedule (o_id, day, start_time, end_time)
            VALUES (%s, %s, %s, %s)
        ''', (o_id, day, start_time, end_time))
        conn.commit()

        flash(_("Course offering added successfully."), "success")
        current_app.logger.info(f"GS {gs_id} added offering for {dept} {number} ({semester} {year}).")

    except pymysql.IntegrityError:
        flash(_("This course offering already exists for that semester and section."), "error")
    except pymysql.Error as e:
        flash(_("Error adding course offering."), "error")
        current_app.logger.error(f"DB error in add_offering: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grad_secretary.schedule'))