"""
Faculty instructor routes: course list, class roster, grade entry, and grade submission.

All routes require an authenticated session with role 'faculty_instructor' or
'system_admin'. Routes are registered on the 'faculty_instructor' blueprint.
"""

from flask import render_template, session, flash, redirect, url_for, request, current_app
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import faculty_instructor
import sqlite3

from flask_babel import _

@faculty_instructor.route('/')
@login_required
@role_required('system_admin', 'faculty_instructor')
def index():
    """
    Render the faculty home dashboard.
    """
    return render_template('faculty_instructor.html')


@faculty_instructor.route('/courses')
@login_required
@role_required('system_admin', 'faculty_instructor')
def courses():
    """
    Render a list of course offerings assigned to the logged-in instructor.

    Joins c_offering with c_catalog and schedule to display course code,
    title, credits, semester, day, and time for each assigned section.
    """
    uid = session['user_id']
    my_courses = []
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        my_courses = cursor.execute('''
            SELECT o.o_id, c.dept, c.number, c.name, c.credits,
                   o.semester, o.year, s.day, s.start_time, s.end_time
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            WHERE o.i_id = ?
        ''', (uid,)).fetchall()

        current_app.logger.info(f"Instructor {uid} accessed their assigned courses list.")
        
    except sqlite3.Error as e:
        flash(_("Error loading courses."), "error")
        current_app.logger.error(f"DB error in faculty courses: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_courses.html', courses=my_courses)


@faculty_instructor.route('/roster')
@login_required
@role_required('system_admin', 'faculty_instructor')
def roster():
    """
    Render the class roster for all courses taught by the logged-in instructor.

    Joins offerings, catalog, enrollment, plan, and users tables to list
    each enrolled student's name, email, and current grade, grouped by course.
    """
    uid = session['user_id']
    roster_data = []
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        roster_data = cursor.execute('''
            SELECT c.dept, c.number, c.name,
                   u.fname || ' ' || u.lname AS student_name,
                   u.email, e.grade
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN enrollment e ON o.o_id = e.o_id
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            WHERE o.i_id = ?
            ORDER BY c.dept, c.number, u.lname
        ''', (uid,)).fetchall()
        
        current_app.logger.info(f"Instructor {uid} accessed their class roster.")
        
    except sqlite3.Error as e:
        flash(_("Error loading roster."), "error")
        current_app.logger.error(f"DB error in faculty roster: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_roster.html', roster=roster_data)


@faculty_instructor.route('/grades')
@login_required
@role_required('system_admin', 'faculty_instructor')
def grades():
    """
    Render the grade entry form for students with in-progress (IP) grades.

    Only shows enrollments where grade='IP', preventing faculty from seeing
    or interacting with already-submitted grades.
    """
    uid = session['user_id']
    students = []
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # only show IP grades — faculty cannot change already submitted grades
        students = cursor.execute('''
            SELECT e.enroll_id, c.dept, c.number, c.name,
                   u.fname || ' ' || u.lname AS student_name,
                   e.grade
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN enrollment e ON o.o_id = e.o_id
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            WHERE o.i_id = ? AND e.grade = 'IP'
            ORDER BY c.dept, c.number, u.lname
        ''', (uid,)).fetchall()

        current_app.logger.info(f"Instructor {uid} accessed the pending grades entry sheet.")
        
    except sqlite3.Error as e:
        flash(_("Error loading grades."), "error")
        current_app.logger.error(f"DB error in faculty grades: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_grades.html', students=students)


@faculty_instructor.route('/submit_grade/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'faculty_instructor')
def submit_grade(enroll_id):
    """
    Submit a final grade for a specific enrollment record (POST only).

    Validates that the grade value is in the allowed set, verifies that the
    enrollment belongs to a course taught by the requesting instructor, and
    confirms the grade is still 'IP' before updating. Rejects attempts to
    overwrite an already-submitted grade.

    Args:
        enroll_id (int): The enrollment record to update.
    """
    uid = session['user_id']
    grade = request.form.get('grade')

    valid_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F'}
    if grade not in valid_grades:
        flash(_("Invalid grade selected."), "error")

        current_app.logger.warning(f"Instructor {uid} attempted to submit an invalid grade ('{grade}') for enrollment {enroll_id}.")
        return redirect(url_for('faculty_instructor.grades'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # verify this enrollment belongs to a course taught by this faculty
        # and that the grade is still IP (cannot overwrite a submitted grade)
        enrollment = cursor.execute('''
            SELECT e.enroll_id, e.grade
            FROM enrollment e
            JOIN c_offering o ON e.o_id = o.o_id
            WHERE e.enroll_id = ? AND o.i_id = ?
        ''', (enroll_id, uid)).fetchone()

        if not enrollment:
            flash(_("You are not authorized to grade this student."), "error")

            current_app.logger.warning(f"Instructor {uid} attempted to submit a grade for enrollment {enroll_id} without authorization.")
            return redirect(url_for('faculty_instructor.grades'))

        if enrollment['grade'] != 'IP':
            flash(_("Grade already submitted and cannot be changed."), "error")
            
            current_app.logger.warning(f"Instructor {uid} attempted to overwrite a locked grade for enrollment {enroll_id}.")
            return redirect(url_for('faculty_instructor.grades'))

        cursor.execute('''
            UPDATE enrollment SET grade = ? WHERE enroll_id = ?
        ''', (grade, enroll_id))
        conn.commit()
        flash(_("Grade submitted successfully."), "success")
        current_app.logger.info(f"Instructor {uid} successfully submitted grade '{grade}' for enrollment {enroll_id}.")

    except sqlite3.Error as e:
        flash(_("A database error occurred."), "error")
        current_app.logger.error(f"DB error submitting grade: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('faculty_instructor.grades'))