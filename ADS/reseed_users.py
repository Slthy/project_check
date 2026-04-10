"""
Clears all user-related rows and re-seeds test users from schema.sql.
Run once from the project root: python reseed_users.py
"""
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.environ['MYSQL_HOST'],
    port=int(os.environ.get('MYSQL_PORT', 3306)),
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASSWORD'],
    database=os.environ['MYSQL_DATABASE'],
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False,
)

cur = conn.cursor()

# --- 1. Clear all user-dependent tables in FK-safe order ---
print("Clearing user-related tables...")
cur.execute("SET FOREIGN_KEY_CHECKS = 0")

for table in [
    'student_enrollments',
    'form1_courses',
    'graduation_applications',
    'form1',
    'alumni',
    'students',
    'system_administrators',
    'faculty',
    'users',
]:
    cur.execute(f"DELETE FROM `{table}`")
    print(f"  Cleared {table} ({cur.rowcount} rows deleted)")

cur.execute("SET FOREIGN_KEY_CHECKS = 1")

# --- 2. Re-insert users and linked records from schema ---
print("\nRe-seeding users...")

statements = [
    # admin1 / adminpass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'admin1', '$2b$12$TUnJTOloSkbkeio/tSvik.zuO8o3K2XM0LRPRoHVmzJWL4D8utFEu', role_id
       FROM roles WHERE role_name = 'admin'""",

    """INSERT INTO system_administrators (user_id, first_name, last_name)
       SELECT user_id, 'System', 'Admin' FROM users WHERE username = 'admin1'""",

    # gs_office / gs_office_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'gs_office', '$2b$12$3sICyD7Ca/l9b8BPcgiL5egq13FXJBov8qoXM5kWGAna2cKg3HZ4W', role_id
       FROM roles WHERE role_name = 'grad_secretary'""",

    # narahari / narahari_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'narahari', '$2b$12$rEo.K4oqmhewDNa1SZxPnuQRjySTkw8ltPH8.a7E5JPdTpn5M8Pzu', role_id
       FROM roles WHERE role_name = 'advisor'""",

    """INSERT INTO faculty (user_id, first_name, last_name)
       SELECT user_id, 'Sridhar', 'Narahari' FROM users WHERE username = 'narahari'""",

    # parmer / parmer_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'parmer', '$2b$12$C8tV2oNLR8vcYrtmuB/sqeEwqpdBr7T.7eNnpwK/zryMl4.yLPkmO', role_id
       FROM roles WHERE role_name = 'advisor'""",

    """INSERT INTO faculty (user_id, first_name, last_name)
       SELECT user_id, 'John', 'Parmer' FROM users WHERE username = 'parmer'""",

    # pmccartney / pmccartney_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'pmccartney', '$2b$12$2L/CiOsVMm8j6ZkbNIWq0egZ4mbTbOIXMuEgMRRlUM3HBAnyrfra6', role_id
       FROM roles WHERE role_name = 'student'""",

    """INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id, faculty_id)
       SELECT u.user_id, '55555555', 'Paul', 'McCartney', '1 Abbey Rd', 'paul.mccartney@gwu.edu', p.program_id, f.faculty_id
       FROM users u
       JOIN programs p ON p.program_code = 'MS'
       LEFT JOIN faculty f ON f.user_id = (SELECT user_id FROM users WHERE username = 'narahari')
       WHERE u.username = 'pmccartney'""",

    # gharrison / gharrison_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'gharrison', '$2b$12$/rDDIwWnvlXqbJftuS9gBewoCBcPFg147OBuZwRF3Ue9bkAJV21z.', role_id
       FROM roles WHERE role_name = 'student'""",

    """INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id, faculty_id)
       SELECT u.user_id, '66666666', 'George', 'Harrison', '2 Abbey Rd', 'george.harrison@gwu.edu', p.program_id, f.faculty_id
       FROM users u
       JOIN programs p ON p.program_code = 'MS'
       LEFT JOIN faculty f ON f.user_id = (SELECT user_id FROM users WHERE username = 'parmer')
       WHERE u.username = 'gharrison'""",

    # rstarr / rstarr_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'rstarr', '$2b$12$jEu/ZFKmi9J0d7UIdp/NB.tp0YO1JRQXtZNSvJJPA0rGWNOdIs4Fq', role_id
       FROM roles WHERE role_name = 'student'""",

    """INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id, faculty_id)
       SELECT u.user_id, '88888888', 'Ringo', 'Starr', '3 Abbey Rd', 'ringo.starr@gwu.edu', p.program_id, f.faculty_id
       FROM users u
       JOIN programs p ON p.program_code = 'PhD'
       LEFT JOIN faculty f ON f.user_id = (SELECT user_id FROM users WHERE username = 'parmer')
       WHERE u.username = 'rstarr'""",

    # eclapton / eclapton_pass
    """INSERT INTO users (username, password_hash, role_id)
       SELECT 'eclapton', '$2b$12$eq9ocvcSUumUmo.8YGOZPuhVOPAlwD3rDmF3SDtExArzldywp0AUu', role_id
       FROM roles WHERE role_name = 'alumni'""",

    """INSERT INTO students (user_id, uid, first_name, last_name, address, email, program_id, faculty_id)
       SELECT u.user_id, '77777777', 'Eric', 'Clapton', '4 Abbey Rd', 'eric.clapton@gwu.edu', p.program_id, f.faculty_id
       FROM users u
       JOIN programs p ON p.program_code = 'MS'
       LEFT JOIN faculty f ON f.user_id = (SELECT user_id FROM users WHERE username = 'narahari')
       WHERE u.username = 'eclapton'""",

    """INSERT INTO alumni (user_id, uid, first_name, last_name, address, email, program_id, graduation_term_id, graduation_year, final_gpa)
       SELECT u.user_id, '77777777', 'Eric', 'Clapton', '4 Abbey Rd', 'eric.clapton@gwu.edu', p.program_id, t.term_id, 2014, 3.30
       FROM users u
       JOIN programs p ON p.program_code = 'MS'
       JOIN terms t ON t.term_name = 'Spring'
       WHERE u.username = 'eclapton'""",

    # --- Transcript enrollments ---
    # pmccartney
    """INSERT INTO student_enrollments (student_id, course_id, term_id, year_taken, grade_id)
       SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
       FROM (
           SELECT 'pmccartney' AS username, 'CSCI' AS dept_code, '6221' AS course_number, 'Fall' AS term_name, 2021 AS year_taken, 'A' AS grade_code
           UNION ALL SELECT 'pmccartney','CSCI','6212','Spring',2022,'A'
           UNION ALL SELECT 'pmccartney','CSCI','6461','Summer',2022,'A'
           UNION ALL SELECT 'pmccartney','CSCI','6232','Fall',2022,'A'
           UNION ALL SELECT 'pmccartney','CSCI','6233','Spring',2023,'A'
           UNION ALL SELECT 'pmccartney','CSCI','6241','Summer',2023,'B'
           UNION ALL SELECT 'pmccartney','CSCI','6246','Fall',2023,'B'
           UNION ALL SELECT 'pmccartney','CSCI','6262','Spring',2024,'B'
           UNION ALL SELECT 'pmccartney','CSCI','6283','Summer',2024,'B'
           UNION ALL SELECT 'pmccartney','CSCI','6242','Fall',2024,'B'
       ) e
       JOIN users u ON u.username = e.username
       JOIN students s ON s.user_id = u.user_id
       JOIN departments d ON d.department_code = e.dept_code
       JOIN courses c ON c.department_id = d.department_id AND c.course_number = e.course_number
       JOIN terms t ON t.term_name = e.term_name
       JOIN grades g ON g.grade_code = e.grade_code""",

    # gharrison
    """INSERT INTO student_enrollments (student_id, course_id, term_id, year_taken, grade_id)
       SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
       FROM (
           SELECT 'gharrison' AS username, 'ECE' AS dept_code, '6242' AS course_number, 'Fall' AS term_name, 2021 AS year_taken, 'C' AS grade_code
           UNION ALL SELECT 'gharrison','CSCI','6221','Spring',2022,'B'
           UNION ALL SELECT 'gharrison','CSCI','6461','Summer',2022,'B'
           UNION ALL SELECT 'gharrison','CSCI','6212','Fall',2022,'B'
           UNION ALL SELECT 'gharrison','CSCI','6232','Spring',2023,'B'
           UNION ALL SELECT 'gharrison','CSCI','6233','Summer',2023,'B'
           UNION ALL SELECT 'gharrison','CSCI','6241','Fall',2023,'B'
           UNION ALL SELECT 'gharrison','CSCI','6242','Spring',2024,'B'
           UNION ALL SELECT 'gharrison','CSCI','6283','Summer',2024,'B'
           UNION ALL SELECT 'gharrison','CSCI','6284','Fall',2024,'B'
       ) e
       JOIN users u ON u.username = e.username
       JOIN students s ON s.user_id = u.user_id
       JOIN departments d ON d.department_code = e.dept_code
       JOIN courses c ON c.department_id = d.department_id AND c.course_number = e.course_number
       JOIN terms t ON t.term_name = e.term_name
       JOIN grades g ON g.grade_code = e.grade_code""",

    # rstarr
    """INSERT INTO student_enrollments (student_id, course_id, term_id, year_taken, grade_id)
       SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
       FROM (
           SELECT 'rstarr' AS username, 'CSCI' AS dept_code, '6212' AS course_number, 'Fall' AS term_name, 2020 AS year_taken, 'A' AS grade_code
           UNION ALL SELECT 'rstarr','CSCI','6221','Spring',2021,'A'
           UNION ALL SELECT 'rstarr','CSCI','6461','Summer',2021,'A'
           UNION ALL SELECT 'rstarr','CSCI','6232','Fall',2021,'A'
           UNION ALL SELECT 'rstarr','CSCI','6233','Spring',2022,'A'
           UNION ALL SELECT 'rstarr','CSCI','6241','Summer',2022,'A'
           UNION ALL SELECT 'rstarr','CSCI','6242','Fall',2022,'A'
           UNION ALL SELECT 'rstarr','CSCI','6246','Spring',2023,'A'
           UNION ALL SELECT 'rstarr','CSCI','6262','Summer',2023,'A'
           UNION ALL SELECT 'rstarr','CSCI','6283','Fall',2023,'A'
           UNION ALL SELECT 'rstarr','CSCI','6284','Spring',2024,'A'
           UNION ALL SELECT 'rstarr','CSCI','6286','Summer',2024,'A'
       ) e
       JOIN users u ON u.username = e.username
       JOIN students s ON s.user_id = u.user_id
       JOIN departments d ON d.department_code = e.dept_code
       JOIN courses c ON c.department_id = d.department_id AND c.course_number = e.course_number
       JOIN terms t ON t.term_name = e.term_name
       JOIN grades g ON g.grade_code = e.grade_code""",

    # eclapton
    """INSERT INTO student_enrollments (student_id, course_id, term_id, year_taken, grade_id)
       SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
       FROM (
           SELECT 'eclapton' AS username, 'CSCI' AS dept_code, '6221' AS course_number, 'Fall' AS term_name, 2011 AS year_taken, 'B' AS grade_code
           UNION ALL SELECT 'eclapton','CSCI','6212','Spring',2012,'B'
           UNION ALL SELECT 'eclapton','CSCI','6461','Summer',2012,'B'
           UNION ALL SELECT 'eclapton','CSCI','6232','Fall',2012,'B'
           UNION ALL SELECT 'eclapton','CSCI','6233','Spring',2013,'B'
           UNION ALL SELECT 'eclapton','CSCI','6241','Summer',2013,'B'
           UNION ALL SELECT 'eclapton','CSCI','6242','Fall',2013,'B'
           UNION ALL SELECT 'eclapton','CSCI','6283','Spring',2014,'A'
           UNION ALL SELECT 'eclapton','CSCI','6284','Spring',2014,'A'
           UNION ALL SELECT 'eclapton','CSCI','6286','Spring',2014,'A'
       ) e
       JOIN users u ON u.username = e.username
       JOIN students s ON s.user_id = u.user_id
       JOIN departments d ON d.department_code = e.dept_code
       JOIN courses c ON c.department_id = d.department_id AND c.course_number = e.course_number
       JOIN terms t ON t.term_name = e.term_name
       JOIN grades g ON g.grade_code = e.grade_code""",
]

for sql in statements:
    cur.execute(sql)
    label = sql.strip().split('\n')[0][:60]
    print(f"  OK ({cur.rowcount} rows): {label}...")

conn.commit()
cur.close()
conn.close()
print("\nDone. All test users re-seeded successfully.")
