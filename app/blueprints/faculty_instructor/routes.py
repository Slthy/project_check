from flask import render_template, session, flash, redirect, url_for, request
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import faculty_instructor
import sqlite3

@faculty_instructor.route('/')
@login_required
@role_required('system_admin', 'faculty_instructor')
def index():
    return render_template('faculty_instructor.html')


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
        my_courses = cursor.execute('''
            SELECT o.o_id, c.dept, c.number, c.name, c.credits,
                   o.semester, o.year, s.day, s.start_time, s.end_time
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            WHERE o.i_id = ?
        ''', (uid,)).fetchall()
    except sqlite3.Error as e:
        flash("Error loading courses.", "error")
        print(f"DB error in faculty courses: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_courses.html', courses=my_courses)


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
    except sqlite3.Error as e:
        flash("Error loading roster.", "error")
        print(f"DB error in faculty roster: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_roster.html', roster=roster_data)


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
    except sqlite3.Error as e:
        flash("Error loading grades.", "error")
        print(f"DB error in faculty grades: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('faculty_grades.html', students=students)


@faculty_instructor.route('/submit_grade/<int:enroll_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'faculty_instructor')
def submit_grade(enroll_id):
    uid = session['user_id']
    grade = request.form.get('grade')

    valid_grades = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F'}
    if grade not in valid_grades:
        flash("Invalid grade selected.", "error")
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
            flash("You are not authorized to grade this student.", "error")
            return redirect(url_for('faculty_instructor.grades'))

        if enrollment['grade'] != 'IP':
            flash("Grade already submitted and cannot be changed.", "error")
            return redirect(url_for('faculty_instructor.grades'))

        cursor.execute('''
            UPDATE enrollment SET grade = ? WHERE enroll_id = ?
        ''', (grade, enroll_id))
        conn.commit()
        flash("Grade submitted successfully.", "success")

    except sqlite3.Error as e:
        flash("A database error occurred.", "error")
        print(f"DB error submitting grade: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('faculty_instructor.grades'))