from flask import render_template, request, session, flash, redirect, url_for, jsonify
from . import staff

import sqlite3

from functions import grade_student

from utils.functions import get_db_connection

from utils.decorators import is_staff

@staff.route('/myStudents', methods=['GET'])
@is_staff
def myStudents(): # just for student list - admin panel
    
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM users"

    if session['role'] == 2 : # professors only see their students
        query += ''' WHERE uid IN (
                    SELECT p.owner_id
                    FROM plan p
                    JOIN enrollment e ON p.plan_id = e.plan_id
                    JOIN c_offering co ON e.o_id = co.o_id
                    WHERE co.i_id = ?
                    );'''

        return jsonify([dict(row) for row in cursor.execute(query, (session['uid'],))])
    else: # roles: 0, 1
        return jsonify([dict(row) for row in cursor.execute(query)])

@staff.route('/grade/<int:o_id>/<int:student_id>', methods=['POST'])
@is_staff
def grade(o_id: int, student_id: int):

    grade = request.form['grade_input']

    conn = get_db_connection()
    cursor = conn.cursor()

    if grade not in ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP']:
        flash('unrecognized grade', 'error')
        return redirect(url_for(''))

    if session['role'] == "2":  # professors can only grade once
        grade = cursor.execute('''
            SELECT e.grade 
            FROM enrollment e
            JOIN c_offering co ON e.o_id = co.o_id
            JOIN c_catalog cc ON co.c_id = cc.c_id
            WHERE e.o_id = ? 
            AND e.plan_id = (
                SELECT plan_id 
                FROM plan 
                WHERE owner_id = ?
            );
        ''', (o_id, student_id)).fetchone()

        if conn:
            conn.close()

        if grade != 'IP':
            flash('faculty_instructor cannot re-grade a course', 'error')
            return redirect(url_for(''))

    success = grade_student(o_id, student_id, grade)
    if success:
        flash('grade updated successfully!', 'success')
    else:
        flash('unrecognized grade or database error', 'error')
        
    return redirect('/')


@staff.route('/students', methods=['GET'])
@is_staff
def get_students(): # actual phase2 query

    admit_year = request.args.get('admit_year')
    track = request.args.get('track')
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT u.uid, u.fname, u.lname, u.email, st.track, st.admit_year
            FROM users u
            JOIN stud_type st ON u.uid = st.uid
            WHERE 1=1 
        ''' # base query, I learned that people use 1=1 as a placeholder to add new constraints dynamically 
        params = [] #http://.../staff/students?admit_year=2024&track=Masters for optional 
        
        if admit_year:
            query += " AND st.admit_year = ?"
            params.append(int(admit_year))
        
        if track:
            query += " AND st.track = ?"
            params.append(track)

        query += " ORDER BY st.admit_year DESC"

        students = cursor.execute(query, params).fetchall()
        
        return jsonify([dict(row) for row in students])

    except sqlite3.Error as e:
        print(f"database error in get_students: {e}")
        return jsonify({"error": "could not retrieve student list."}), 500

    finally:
        if conn:
            conn.close()