"""
Faculty instructor routes: course list, class roster, grade entry, and grade submission.

All routes require an authenticated session with role 'faculty_instructor' or
'system_admin'. Routes are registered on the 'faculty_instructor' blueprint.
"""

from flask import render_template, session, flash, redirect, url_for, request, current_app
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import faculty_instructor
import pymysql

from flask_babel import _

@faculty_instructor.route('/')
@login_required
@role_required('system_admin', 'faculty_instructor')
def index():
    return render_template('faculty_instructor/faculty_instructor.html')


@faculty_instructor.route('/courses')
@login_required
@role_required('system_admin', 'faculty_instructor')
def courses():
    uid = session['user_id']
    my_courses = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.o_id, c.dept, c.number, c.name, c.credits,
                   o.semester, o.year, s.day, s.start_time, s.end_time
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            WHERE o.i_id = %s
        ''', (uid,))
        my_courses = cursor.fetchall()
        current_app.logger.info(f"Instructor {uid} accessed their assigned courses list.")
    except pymysql.Error as e:
        flash(_("Error loading courses."), "error")
        current_app.logger.error(f"DB error in faculty courses: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('faculty_instructor/faculty_courses.html', courses=my_courses)


@faculty_instructor.route('/roster')
@login_required
@role_required('system_admin', 'faculty_instructor')
def roster():
    uid = session['user_id']
    roster_data = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.dept, c.number, c.name,
                   CONCAT(u.fname, " ", u.lname) AS student_name,
                   u.email, e.grade
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN enrollment e ON o.o_id = e.o_id
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            WHERE o.i_id = %s
            ORDER BY c.dept, c.number, u.lname
        ''', (uid,))
        roster_data = cursor.fetchall()
        current_app.logger.info(f"Instructor {uid} accessed their class roster.")
    except pymysql.Error as e:
        flash(_("Error loading roster."), "error")
        current_app.logger.error(f"DB error in faculty roster: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('faculty_instructor/faculty_roster.html', roster=roster_data)


@faculty_instructor.route('/grades')
@login_required
@role_required('system_admin', 'faculty_instructor')
def grades():
    uid = session['user_id']
    students = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.enroll_id, c.dept, c.number, c.name,
                   CONCAT(u.fname, " ", u.lname) AS student_name,
                   e.grade
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN enrollment e ON o.o_id = e.o_id
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN users u ON p.owner_id = u.id
            WHERE o.i_id = %s AND e.grade = 'IP'
            ORDER BY c.dept, c.number, u.lname
        ''', (uid,))
        students = cursor.fetchall()
        current_app.logger.info(f"Instructor {uid} accessed the pending grades entry sheet.")
    except pymysql.Error as e:
        flash(_("Error loading grades."), "error")
        current_app.logger.error(f"DB error in faculty grades: {e}")
    finally:
        if conn:
            conn.close()
    return render_template('faculty_instructor/faculty_grades.html', students=students)


@faculty_instructor.route('/submit_grade/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'faculty_instructor')
def submit_grade(enroll_id):
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
        cursor.execute('''
            SELECT e.enroll_id, e.grade
            FROM enrollment e
            JOIN c_offering o ON e.o_id = o.o_id
            WHERE e.enroll_id = %s AND o.i_id = %s
        ''', (enroll_id, uid))
        enrollment = cursor.fetchone()

        if not enrollment:
            flash(_("You are not authorized to grade this student."), "error")
            current_app.logger.warning(f"Instructor {uid} attempted to submit a grade for enrollment {enroll_id} without authorization.")
            return redirect(url_for('faculty_instructor.grades'))

        if enrollment['grade'] != 'IP':
            flash(_("Grade already submitted and cannot be changed."), "error")
            current_app.logger.warning(f"Instructor {uid} attempted to overwrite a locked grade for enrollment {enroll_id}.")
            return redirect(url_for('faculty_instructor.grades'))

        cursor.execute(
            'UPDATE enrollment SET grade = %s WHERE enroll_id = %s',
            (grade, enroll_id)
        )
        conn.commit()
        flash(_("Grade submitted successfully."), "success")
        current_app.logger.info(f"Instructor {uid} successfully submitted grade '{grade}' for enrollment {enroll_id}.")
    except pymysql.Error as e:
        flash(_("A database error occurred."), "error")
        current_app.logger.error(f"DB error submitting grade: {e}")
    finally:
        if conn:
            conn.close()
    return redirect(url_for('faculty_instructor.grades'))