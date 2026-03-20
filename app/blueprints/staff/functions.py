from flask import render_template, request, session, flash, redirect

import sqlite3

from utils.functions import get_db_connection

def grade_student(o_id: int, student_id: int, grade: str):
    """
    Check faculty_instructor contraints if needed, grade student

    Args:
        o_id (int): Offering's id.
        student_id (int): Student's id.
        grade (str): student's grade.

    Returns:
        Union[int, str]: returns '0' if the grade has been inserted correctly or why the course hasn't been updated
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            UPDATE enrollment
            SET grade = ?
            WHERE o_id = ?
              AND plan_id = (
                  SELECT plan_id
                  FROM plan
                  WHERE owner_id = ?
              );
        ''', (grade, o_id, student_id))

        conn.commit()

        if cursor.rowcount > 0:
            print(f"grade updated to {grade} for student {student_id} in offering {o_id}.")
            return True
        else:
            print("no record found to update.")
            return False

    except sqlite3.IntegrityError as e:
        print(f"invalid grade provided: {e}")
        return False
        
    except sqlite3.Error as e:
        print(f"database error: {e}")
        return False

    finally:
        if conn:
            conn.close()