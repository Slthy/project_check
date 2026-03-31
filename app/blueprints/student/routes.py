"""
Student-facing routes: course browser, transcript, add course, and drop course.

All routes require an authenticated session with role 'student' or
'system_admin'. Routes are registered on the 'student' blueprint under /student.
"""

from flask import render_template, session, flash, redirect, url_for, current_app
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection, has_time_conflict
from . import student
import sqlite3
from flask_babel import _

@student.route('/')
@login_required
@role_required('system_admin', 'student')
def index():
    """
    Render the course browser with eligibility status for each offering.

    Fetches the student's current schedule (in-progress enrollments) and
    completed course IDs to determine, for every available offering, whether
    the student is already enrolled, is missing prerequisites, has a time
    conflict, or is eligible to register. Passes both the full offering list
    (with status) and the current schedule table to the template.
    """
    uid = session['user_id']
    conn = None
    all_courses = []
    current_courses = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # get student's current schedule (IP courses)
        current_schedule = cursor.execute('''
            SELECT s.day, s.start_time, s.end_time, o.o_id
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN schedule s ON o.o_id = s.o_id
            WHERE p.owner_id = ? AND e.grade = 'IP'
        ''', (uid,)).fetchall()

        current_o_ids = {row['o_id'] for row in current_schedule}

        # get completed course c_ids (for prereq checking)
        completed_cids = {row['c_id'] for row in cursor.execute('''
            SELECT o.c_id
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN c_offering o ON e.o_id = o.o_id
            WHERE p.owner_id = ? AND e.grade != 'IP'
        ''', (uid,)).fetchall()}

        # get all offerings with instructor and schedule
        offerings = cursor.execute('''
            SELECT o.o_id, o.c_id, o.semester, o.year,
                   c.dept, c.number, c.name, c.credits,
                   c.prereq1_id, c.prereq2_id,
                   u.fname || ' ' || u.lname AS instructor,
                   s.day, s.start_time, s.end_time
            FROM c_offering o
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN users u ON o.i_id = u.id
            LEFT JOIN schedule s ON o.o_id = s.o_id
        ''').fetchall()

        for course in offerings:
            # check prereqs
            missing = []
            for prereq_id in [course['prereq1_id'], course['prereq2_id']]:
                if prereq_id and prereq_id not in completed_cids:
                    prereq = cursor.execute(
                        'SELECT dept, number FROM c_catalog WHERE c_id = ?', (prereq_id,)
                    ).fetchone()
                    if prereq:
                        missing.append(f"{prereq['dept']} {prereq['number']}")

            if course['o_id'] in current_o_ids:
                status = 'Enrolled'
            elif missing:
                status = f"Missing: {', '.join(missing)}"
            elif has_time_conflict(current_schedule, [course]):
                status = 'Time conflict'
            else:
                status = 'Eligible'

            all_courses.append({**dict(course), 'status': status})

        # get current schedule for bottom table
        current_courses = cursor.execute('''
            SELECT o.o_id, c.dept, c.number, c.name,
                   s.day, s.start_time, s.end_time
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            LEFT JOIN schedule s ON o.o_id = s.o_id
            WHERE p.owner_id = ? AND e.grade = 'IP'
        ''', (uid,)).fetchall()

        current_app.logger.info(f"Student {uid} accessed the course browser.")

    except sqlite3.Error as e:
        flash(_("Error loading courses."), "error")
        current_app.logger.error(f"DB error in index: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('courses.html', all_courses=all_courses, current_courses=current_courses)


@student.route('/transcript')
@login_required
@role_required('system_admin', 'student')
def transcript():
    """
    Render the student's academic transcript with GPA summary.

    Retrieves all enrollment records for the logged-in student, filters to
    completed courses (grade != 'IP') to compute total earned credits and
    weighted GPA, and passes the full course list and summary stats to the
    template.
    """
    uid = session['user_id']
    all_courses = []
    conn = None

    GRADE_POINTS = {
        'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0,
        'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'F': 0.0
    }

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.dept, c.number, c.name, c.credits,
                   e.grade, o.semester, o.year
            FROM enrollment e
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN c_catalog c ON o.c_id = c.c_id
            JOIN plan p ON e.plan_id = p.plan_id
            WHERE p.owner_id = ?
            ORDER BY o.year, o.semester
        ''', (uid,))
        all_courses = cursor.fetchall()
        
        current_app.logger.info(f"Student {uid} accessed their academic transcript.")
        
    except sqlite3.Error as e:
        current_app.logger.error(f"DB error in index: {e}")
    finally:
        if conn:
            conn.close()

    # calculate summary stats
    total_credits = 0
    total_points = 0.0
    completed = [c for c in all_courses if c['grade'] != 'IP']

    for course in completed:
        credits = course['credits']
        grade_pts = GRADE_POINTS.get(course['grade'], 0.0)
        total_credits += credits
        total_points += grade_pts * credits

    gpa = round(total_points / total_credits, 2) if total_credits > 0 else 0.0

    return render_template('transcript.html',
                           all_courses=all_courses,
                           total_credits=total_credits,
                           gpa=gpa)


@student.route('/drop_course/<int:o_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'student')
def drop_course(o_id):
    """
    Drop the student from a specific course offering (POST only).

    Deletes the enrollment row matching the offering ID and the student's
    plan. Flashes a success message if a row was deleted, or an error if no
    matching enrollment was found.

    Args:
        o_id (int): The offering ID to drop.
    """
    uid = session['user_id']
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM enrollment
            WHERE o_id = ?
              AND plan_id = (SELECT plan_id FROM plan WHERE owner_id = ?)
        ''', (o_id, uid))
        conn.commit()

        if cursor.rowcount > 0:
            flash(_("Course successfully dropped."), "success")
            
            current_app.logger.info(f"Student {uid} successfully dropped offering {o_id}.")
        else:
            flash(_("Could not drop the course. Are you sure you are enrolled?"), "error")
            
            current_app.logger.warning(f"Student {uid} failed to drop offering {o_id} (not enrolled).")

    except sqlite3.Error as e:
        flash(_("A database error occurred while dropping the course."), "error")
        current_app.logger.error(f"DB error dropping course {o_id} for user {uid}: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('student.index'))


@student.route('/add_course/<int:o_id>', methods=['POST'])
@login_required
@role_required('system_admin', 'student')
def add_course(o_id):
    """
    Enroll the student in a specific course offering (POST only).

    Performs three server-side checks before inserting the enrollment row:
    1. Verifies the offering exists.
    2. Checks that all prerequisites have been completed with a non-IP grade.
    3. Checks for schedule conflicts with the student's current timetable.

    Flashes appropriate error messages if any check fails. On success, inserts
    an enrollment row with grade='IP' linked to the student's plan.

    Args:
        o_id (int): The offering ID to enroll in.
    """
    uid = session['user_id']
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        current_schedule = cursor.execute('''
            SELECT s.day, s.start_time, s.end_time
            FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN c_offering o ON e.o_id = o.o_id
            JOIN schedule s ON o.o_id = s.o_id
            WHERE p.owner_id = ? AND e.grade = 'IP'
        ''', (uid,)).fetchall()

        course_info = cursor.execute(
            'SELECT c_id FROM c_offering WHERE o_id = ?', (o_id,)
        ).fetchone()

        if not course_info:
            flash(_("Course offering not found."), "error")
            
            current_app.logger.warning(f"Student {uid} attempted to enroll in non-existent offering {o_id}.")
            return redirect(url_for('student.index'))

        c_id = course_info['c_id']

        # check prereqs
        prereqs = cursor.execute(
            'SELECT prereq1_id, prereq2_id FROM c_catalog WHERE c_id = ?', (c_id,)
        ).fetchone()

        completed_cids = {row['c_id'] for row in cursor.execute('''
            SELECT o.c_id FROM enrollment e
            JOIN plan p ON e.plan_id = p.plan_id
            JOIN c_offering o ON e.o_id = o.o_id
            WHERE p.owner_id = ? AND e.grade != 'IP'
        ''', (uid,)).fetchall()}

        missing = []
        for prereq_id in [prereqs['prereq1_id'], prereqs['prereq2_id']]:
            if prereq_id and prereq_id not in completed_cids:
                prereq = cursor.execute(
                    'SELECT dept, number FROM c_catalog WHERE c_id = ?', (prereq_id,)
                ).fetchone()
                if prereq:
                    missing.append(f"{prereq['dept']} {prereq['number']}")

        if missing:
            flash(_("Missing prerequisites: %(prereqs)s", prereqs=', '.join(missing)), "error")
            
            current_app.logger.warning(f"Student {uid} failed prerequisite check for offering {o_id}. Missing: {', '.join(missing)}.")
            return redirect(url_for('student.index'))

        new_course_times = cursor.execute(
            'SELECT day, start_time, end_time FROM schedule WHERE o_id = ?', (o_id,)
        ).fetchall()

        if has_time_conflict(current_schedule, new_course_times):
            flash(_("Time conflict! You must have at least 30 minutes between classes."), "error")
            
            current_app.logger.warning(f"Student {uid} experienced a time conflict when attempting to add offering {o_id}.")
            return redirect(url_for('student.index'))

        cursor.execute('''
            INSERT INTO enrollment (plan_id, o_id, grade)
            VALUES ((SELECT plan_id FROM plan WHERE owner_id = ?), ?, 'IP')
        ''', (uid, o_id))
        conn.commit()
        flash(_("Course successfully added!"), "success")
        
        current_app.logger.info(f"Student {uid} successfully enrolled in offering {o_id}.")

    except sqlite3.IntegrityError:
        flash(_("You are already enrolled in this course."), "error")
        
        current_app.logger.warning(f"Student {uid} attempted to enroll in offering {o_id} but is already enrolled.")
    except sqlite3.Error as e:
        flash(_("A database error occurred."), "error")
        current_app.logger.error(f"DB error in add_course: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('student.index'))