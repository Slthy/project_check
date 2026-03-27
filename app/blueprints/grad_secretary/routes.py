from flask import render_template, request, flash, redirect, url_for, session
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import grad_secretary
import sqlite3

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
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        students = cursor.execute('''
            SELECT u.id, u.fname || ' ' || u.lname AS name,
                   u.email, st.track, st.admit_year
            FROM users u
            JOIN stud_type st ON u.id = st.id
            WHERE u.role = 3
            ORDER BY u.lname
        ''').fetchall()
    except sqlite3.Error as e:
        flash("Error loading student records.", "error")
        print(f"DB error in gs records: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_records.html', students=students)


@grad_secretary.route('/records/<int:uid>')
@login_required
@role_required('system_admin', 'grad_secretary')
def student_transcript(uid):
    student = None
    courses = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        student = cursor.execute(
            'SELECT fname, lname, email FROM users WHERE id = ?', (uid,)
        ).fetchone()
        courses = cursor.execute('''
            SELECT c.dept, c.number, c.name, c.credits,
                   e.grade, o.semester, o.year
            FROM enrollment e
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN plan p ON e.plan_id = p.plan_id
            WHERE p.owner_id = ?
            ORDER BY o.year, o.semester
        ''', (uid,)).fetchall()
    except sqlite3.Error as e:
        flash("Error loading transcript.", "error")
        print(f"DB error in gs transcript: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_transcript.html', student=student, courses=courses)


@grad_secretary.route('/schedule')
@login_required
@role_required('system_admin', 'grad_secretary')
def schedule():
    courses = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        courses = cursor.execute('''
            SELECT c.dept, c.number, c.name, c.credits,
                   o.semester, o.year, s.day, s.start_time, s.end_time,
                   u.fname || ' ' || u.lname AS instructor
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            LEFT JOIN users u ON o.i_id = u.id
            ORDER BY s.day, s.start_time
        ''').fetchall()
    except sqlite3.Error as e:
        flash("Error loading schedule.", "error")
        print(f"DB error in gs schedule: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_schedule.html', courses=courses)


@grad_secretary.route('/override-grades')
@login_required
@role_required('system_admin', 'grad_secretary')
def override_grades():
    enrollments = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        enrollments = cursor.execute('''
            SELECT e.enroll_id, u.fname || ' ' || u.lname AS student_name,
                   c.dept, c.number, c.name, e.grade
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            ORDER BY u.lname, c.dept, c.number
        ''').fetchall()
    except sqlite3.Error as e:
        flash("Error loading grades.", "error")
        print(f"DB error in gs override grades: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_override_grades.html', enrollments=enrollments)


@grad_secretary.route('/override-grades/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'grad_secretary')
def submit_override(enroll_id):
    grade = request.form.get('grade')
    valid_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP'}

    if grade not in valid_grades:
        flash("Invalid grade selected.", "error")
        return redirect(url_for('grad_secretary.override_grades'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE enrollment SET grade = ? WHERE enroll_id = ?',
            (grade, enroll_id)
        )
        conn.commit()
        flash("Grade updated successfully.", "success")
    except sqlite3.Error as e:
        flash("A database error occurred.", "error")
        print(f"DB error in gs submit_override: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grad_secretary.override_grades'))