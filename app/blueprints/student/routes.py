from flask import render_template, session, flash, redirect, url_for
from . import student
from .functions import *
import sqlite3

from utils.functions import get_db_connection, has_time_conflict
from utils.decorators import login_required, role_required

@student.route('/<int:uid>', methods=['GET'])
@login_required
def show_user_profile(uid):
    if session.get('role') == 3 and session.get('uid') != uid: # check that a student only asks his/her transcript
        flash("student: uid mismatch", "error")
        return redirect('/')

    conn = None
    user_info = None
    past_courses = None
    current_courses = None

    try: # get student's info
        conn = get_db_connection()
        cursor = conn.cursor()

        user_info = get_user_info(cursor, uid)

        if session.get('role') in [0, 1, 3]:
            past_courses = []
            current_courses = []
            for course in get_student_courses(cursor, uid):
                if course['grade'] == 'IP':
                    current_courses.append(course)
                else:
                    past_courses.append(course)

    except sqlite3.Error as e:
        flash("error loading profile.", "error")
        print(f"DB error in show_user_profile: {e}")

    finally:
        if conn:
            conn.close()

    return render_template('student.html', info=user_info, past_courses=past_courses, current_courses=current_courses)

@student.route('/drop_course/<int:o_id>', methods=['POST'])
@role_required('system_admin', 'student')
def drop_course(o_id):

    uid = session['uid']
    conn = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM enrollment
            WHERE o_id = ?
              AND plan_id = (
                  SELECT plan_id
                  FROM plan
                  WHERE owner_id = ?
              );
        ''', (o_id, uid))

        conn.commit()

        if cursor.rowcount > 0:
            flash("course successfully dropped.", "success")
        else:
            flash("could not drop the course. Are you sure you are enrolled in it?", "error")

    except sqlite3.Error as e:
        flash("a database error occurred while trying to drop the course.", "error")
        print(f"database error dropping course {o_id} for user {uid}: {e}")

    finally:
        if conn:
            conn.close()

    return redirect(url_for('student.show_user_profile', uid=uid))
@student.route('/add_course/<int:o_id>', methods=['POST'])
@role_required('system_admin', 'student')
def add_course(o_id):

    uid = session['uid']
    conn = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        current_schedule = get_student_schedule(cursor, uid)

        course_info = cursor.execute('''
            SELECT c_id FROM c_offering WHERE o_id = ?
        ''', (o_id,)).fetchone()

        if not course_info:
            flash("Course offering not found.", "error")
            return redirect(url_for('student.show_user_profile', uid=uid))            
        c_id = course_info['c_id']

        prereqs = get_course_prereqs(cursor, c_id)
        
        if prereqs:
            
            completed_cids = get_passed_courses(cursor, uid)

            missing_prereqs = []
            for p in prereqs:
                if p['c_id'] not in completed_cids:
                    missing_prereqs.append(f"{p['dept']} {p['number']}")

            if missing_prereqs:
                flash(f"Cannot add course. You are missing prerequisites: {', '.join(missing_prereqs)}", "error")
                return redirect(url_for('student.show_user_profile', uid=uid))
        new_course_times = cursor.execute('''
            SELECT day, start_time, end_time 
            FROM schedule 
            WHERE o_id = ?
        ''', (o_id,)).fetchall()

        if not new_course_times:
            flash("course schedule not found. It might not have meeting times.", "error")
            return redirect(url_for('student.show_user_profile', uid=uid))
        if has_time_conflict(current_schedule, new_course_times):
            flash("time conflict! you must have at least 30 minutes between classes.", "error")
            # ugly functionality "for free": you cannot the same course twice, it would raise a time conflict
            return redirect(url_for('student.show_user_profile', uid=uid))
        cursor.execute('''
            INSERT INTO enrollment (plan_id, o_id, grade)
            VALUES (
                (SELECT plan_id FROM plan WHERE owner_id = ?), ?, 'IP'
            )
        ''', (uid, o_id))

        conn.commit()
        flash("course successfully added to your plan!", "success")

    except sqlite3.IntegrityError:
        flash("you are already enrolled in this course.", "error")
        
    except sqlite3.Error as e:
        flash("a database error occurred.", "error")
        print(f"DB error in add_course: {e}")

    finally:
        if conn:
            conn.close()

    return redirect(f'/{uid}')