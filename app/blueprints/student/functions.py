import sqlite3

def get_student_courses(cursor: sqlite3.Cursor, uid: int):
    try:
        return cursor.execute('''
            SELECT c.*, e.grade, e.enrolled_at
            FROM enrollment e
            JOIN c_offering c ON e.o_id = c.o_id
            WHERE e.plan_id = (
                SELECT plan_id 
                FROM plan 
                WHERE owner_id = ?
            );
        ''', (uid,)).fetchall()
        
    except sqlite3.Error as e:
        print(f"database error in get_student_courses for uid {uid}: {e}")
        return [] 

def get_user_info(cursor: sqlite3.Cursor, uid: int):
    try:
        return cursor.execute('''
            SELECT * FROM users WHERE uid = ?
        ''', (uid,)).fetchone()
        
    except sqlite3.Error as e:
        print(f"database error in get_user_info for uid {uid}: {e}")
        return None

def get_student_schedule(cursor: sqlite3.Cursor, uid: int):
    schedule_dict = {
        'M': [], 
        'T': [], 
        'W': [], 
        'R': [], 
        'F': []
    }
    
    conn = None
    try:

        rows = cursor.execute('''
            SELECT s.day, s.start_time, s.end_time
            FROM schedule s
            JOIN enrollment e ON s.o_id = e.o_id
            JOIN plan p ON e.plan_id = p.plan_id
            WHERE p.owner_id = ?
            ORDER BY s.day, s.start_time;
        ''', (uid,)).fetchall()


        for row in rows:
            day = row['day']
            start = row['start_time']
            end = row['end_time']
            
            if day in schedule_dict:
                schedule_dict[day].append((start, end))

    except sqlite3.Error as e:
        print(f"Database error while fetching schedule for user {uid}: {e}")
        return None

    finally:
        if conn:
            conn.close()

    return schedule_dict

def get_course_prereqs(cursor: sqlite3.Cursor, c_id: int):
    prereqs = []
    
    try:
        rows = cursor.execute('''
            SELECT c_id, dept, number, name, credits
            FROM c_catalog
            WHERE c_id IN (
                SELECT prereq1_id FROM c_catalog WHERE c_id = ?
                UNION
                SELECT prereq2_id FROM c_catalog WHERE c_id = ?
            );
        ''', (c_id, c_id)).fetchall() # 'union' to combine both prereq IDs into a single list

        prereqs = [dict(row) for row in rows] # list of dicts

    except sqlite3.Error as e:
        print(f"Database error while fetching prerequisites for course {c_id}: {e}")

    return prereqs

def get_passed_courses(cursor: sqlite3.Cursor, uid: int):
    passed_cids = set() 
    
    try:
        all_student_courses = get_student_courses(cursor, uid)
        passed_cids = { row['c_id'] for row in all_student_courses if row['grade'] not in ('F', 'IP') }

    except Exception as e:
        print(f"error while fetching passed courses for user {uid}: {e}")

    return passed_cids