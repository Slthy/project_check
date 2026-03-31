"""
Graduate secretary routes: student records, transcripts, course schedule, and grade overrides.

All routes require an authenticated session with role 'grad_secretary' or
'system_admin'. Routes are registered on the 'grad_secretary' blueprint.
"""

from flask import render_template, request, flash, redirect, url_for, current_app, session
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import grad_secretary
import sqlite3

from flask_babel import _

@grad_secretary.route('/')
@login_required
@role_required('system_admin', 'grad_secretary')
def index():
    """
    Redirect to the student records list.
    """
    return redirect(url_for('grad_secretary.records'))

@grad_secretary.route('/records')
@login_required
@role_required('system_admin', 'grad_secretary')
def records():
    """
    Render a list of all registered graduate students.

    Joins the users and stud_type tables to display each student's ID,
    full name, email, program track, and admit year, ordered by last name.
    """
    students = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    
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

        current_app.logger.info(f"Grad Secretary {gs_id} accessed the global student records list.")
        
    except sqlite3.Error as e:
        flash(_("Error loading student records."), "error")
        current_app.logger.error(f"DB error in gs records: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_records.html', students=students)


@grad_secretary.route('/records/<int:uid>')
@login_required
@role_required('system_admin', 'grad_secretary')
def student_transcript(uid):
    """
    Render the academic transcript for a specific student.

    Retrieves the student's name and email alongside all their enrollment
    records, joined with offering and catalog data, ordered chronologically.

    Args:
        uid (int): The user ID of the student whose transcript to display.
    """
    student = None
    courses = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    
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

        current_app.logger.info(f"Grad Secretary {gs_id} accessed the transcript for student ID {uid}.")
        
    except sqlite3.Error as e:
        flash(_("Error loading transcript."), "error")
        current_app.logger.error(f"DB error in gs transcript: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_transcript.html', student=student, courses=courses)


@grad_secretary.route('/schedule')
@login_required
@role_required('system_admin', 'grad_secretary')
def schedule():
    """
    Render the full course schedule for the current semester.

    Joins offerings, catalog, schedule, and users tables to display each
    section's course code, title, credits, semester, day, time slot, and
    instructor name (or 'TBA' if unassigned), ordered by day and start time.
    """
    courses = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    
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
        current_app.logger.info(f"Grad Secretary {gs_id} accessed the full course schedule.")
        
    except sqlite3.Error as e:
        flash(_("Error loading schedule."), "error")
        current_app.logger.error(f"DB error in gs schedule: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_schedule.html', courses=courses)


@grad_secretary.route('/override-grades')
@login_required
@role_required('system_admin', 'grad_secretary')
def override_grades():
    """
    Render the grade override form listing all enrollment records.

    Unlike the faculty grade view, this includes all grades (not just IP),
    allowing the GS to correct any submitted grade at any time.
    """
    enrollments = []
    conn = None
    gs_id = session.get('user_id', 'Unknown')
    
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

        current_app.logger.info(f"Grad Secretary {gs_id} accessed the grade override master list.")
        
    except sqlite3.Error as e:
        flash(_("Error loading grades."), "error")
        current_app.logger.error(f"DB error in gs override grades: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('gs_override_grades.html', enrollments=enrollments)


@grad_secretary.route('/override-grades/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'grad_secretary')
def submit_override(enroll_id):
    """
    Apply a grade override for a specific enrollment record (POST only).

    Validates the submitted grade against the full allowed set (including IP),
    then updates the enrollment row directly. No ownership or lock checks are
    applied — the GS has unrestricted grade editing authority.

    Args:
        enroll_id (int): The enrollment record to update.
    """
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
            'UPDATE enrollment SET grade = ? WHERE enroll_id = ?',
            (grade, enroll_id)
        )
        conn.commit()
        flash(_("Grade updated successfully."), "success")

        current_app.logger.info(f"Grad Secretary {gs_id} successfully overrode grade to '{grade}' for enrollment {enroll_id}.")
        
    except sqlite3.Error as e:
        flash(_("A database error occurred."), "error")
        current_app.logger.error(f"DB error in gs submit_override: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('grad_secretary.override_grades'))