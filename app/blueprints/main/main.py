import sqlite3
from flask import Blueprint, render_template, jsonify, session, flash, redirect

from student import functions as student_functions

from utils.functions import get_db_connection
from utils.decorators import login_required, role_required
from utils.constants import GRADE_SCALE

main = Blueprint('main', __name__) # blueprint object

@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main.route('/trascript/<int:uid>', methods=['GET'])
@role_required('system_admin', 'grad_secretary', 'student')
def trascript(uid: int):
    if session.get('role') == 3 and session.get('uid') != uid: # check that a student only asks his/her transcript
        flash("student: uid mismatch", "error")
        return redirect('/') 
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        all_courses = student_functions.get_student_courses(cursor, uid)
        
        courses_list = []
        total_grade_points = 0.0
        total_credits = 0
        
        for row in all_courses:
            course_dict = dict(row)
            courses_list.append(course_dict)
            
            grade = course_dict['grade']
            credits = course_dict['credits']

            if grade != 'IP' and grade in GRADE_SCALE:
                total_grade_points += (GRADE_SCALE[grade] * credits)
                total_credits += credits
                
        if total_credits > 0:
            final_gpa = round(total_grade_points / total_credits, 2) # gw rounds to 2 sigfigs
        else:
            final_gpa = 0.0
    
        return jsonify({ 'courses': courses_list, 'gpa': final_gpa })

    except sqlite3.Error as e:
        print(f"Database error in my_academic_record: {e}")
        return jsonify({"error": "Could not retrieve academic record at this time."}), 500

    finally:
        if conn:
            conn.close()


@main.route('/about_me', methods=['GET'])
@login_required
def about_me():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        uid = session.get('uid') # safer, returns None and doesn't crash if for some reason the session got cleared

        user = cursor.execute(
            'SELECT * FROM users WHERE uid = ?', (uid,)
        ).fetchone()

        if user:
            return render_template('about_me.html', data=user)
        else:
            flash("User profile not found.", "error")
            return redirect('/')

    except sqlite3.Error as e:
        print(f"Database error in about_me: {e}")
        flash("Could not load your profile at this time.", "error")
        return redirect('/')

    finally:
        if conn:
            conn.close()


@main.route('/get_courses', methods=['GET'])
@login_required
def get_courses():
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        courses = cursor.execute('''
            SELECT 
                co.o_id, co.semester, co.year, co.section, co.location, co.capacity,
                cc.dept, cc.number, cc.name, cc.credits
            FROM c_offering co
            JOIN c_catalog cc ON co.c_id = cc.c_id
        ''').fetchall()

        courses_list = [dict(row) for row in courses]   # list of dicts

        return jsonify(courses_list)

    except sqlite3.Error as e:
        print(f"Database error in get_courses: {e}")
        return jsonify({"error": "Could not retrieve courses at this time."}), 500 # safer: json error, http code

    finally:
        if conn:
            conn.close()