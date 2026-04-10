import re

from academic import get_total_completed_credits

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


# Return True for an empty string (email is optional) or a valid email pattern.
def is_valid_email(email):
    normalized = (email or '').strip()
    if not normalized:
        return True
    return bool(_EMAIL_RE.match(normalized))


# Return 'Thesis Defense' for PhD students, 'Form 1' for all others.
def get_form_label(program_code):
    normalized_program = (program_code or '').strip().upper()
    return 'Thesis Defense' if normalized_program == 'PHD' else 'Form 1'


# Fetch profile fields needed for the student profile edit form.
def get_editable_student_profile(db, user_id):
    return db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            s.address,
            s.email,
            u.username,
            p.program_code,
            p.program_name
        FROM students s
        JOIN users u ON u.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.user_id = %s
        ''',
        (user_id,)
    ).fetchone()


# Fetch full student profile including assigned advisor name.
def get_student_profile_with_advisor_by_user_id(db, user_id):
    return db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            s.address,
            s.email,
            u.username,
            p.program_code,
            p.program_name,
            f.first_name AS advisor_first_name,
            f.last_name AS advisor_last_name
        FROM students s
        JOIN users u ON u.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        LEFT JOIN faculty f ON f.faculty_id = s.faculty_id
        WHERE s.user_id = %s
        ''',
        (user_id,)
    ).fetchone()


# Fetch minimal student and program data needed for Form 1 operations.
def get_student_form1_context_by_user_id(db, user_id):
    return db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            s.program_id,
            p.program_code,
            p.program_name
        FROM students s
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.user_id = %s
        ''',
        (user_id,)
    ).fetchone()


# Fetch all enrollment rows ordered by year and term for transcript display.
def get_transcript_rows(db, student_id):
    return db.execute(
        '''
        SELECT
            c.course_id,
            d.department_code,
            c.course_number,
            c.title,
            c.credit_hours,
            t.term_name,
            se.year_taken,
            g.grade_code,
            g.grade_points
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN departments d ON d.department_id = c.department_id
        JOIN terms t ON t.term_id = se.term_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
        ORDER BY
            se.year_taken DESC,
            t.term_id DESC,
            d.department_code,
            c.course_number
        ''',
        (student_id,)
    ).fetchall()


# Fetch the student's most recent Form 1 submission.
def get_latest_form1(db, student_id):
    return db.execute(
        '''
        SELECT form1_id, student_id, audit_passed, advisor_decision AS review_status
        FROM form1
        WHERE student_id = %s
        ORDER BY form1_id DESC
        LIMIT 1
        ''',
        (student_id,)
    ).fetchone()


# Return the list of course IDs on a given Form 1.
def get_form1_course_ids(db, form1_id):
    return [
        row['course_id']
        for row in db.execute(
            '''
            SELECT course_id
            FROM form1_courses
            WHERE form1_id = %s
            ''',
            (form1_id,)
        ).fetchall()
    ]


# Fetch course details for all courses on a given Form 1.
def get_form1_courses_detailed(db, form1_id):
    return db.execute(
        '''
        SELECT
            c.course_id,
            d.department_code,
            c.course_number,
            c.title,
            c.credit_hours
        FROM form1_courses fc
        JOIN courses c ON c.course_id = fc.course_id
        JOIN departments d ON d.department_id = c.department_id
        WHERE fc.form1_id = %s
        ORDER BY d.department_code, c.course_number
        ''',
        (form1_id,)
    ).fetchall()


# Return distinct course IDs from the student's transcript.
def get_transcript_course_ids(db, student_id):
    return [
        row['course_id']
        for row in db.execute(
            '''
            SELECT DISTINCT se.course_id
            FROM student_enrollments se
            WHERE se.student_id = %s
            ''',
            (student_id,)
        ).fetchall()
    ]


# Fetch the student's most recent graduation application.
def get_latest_graduation_application(db, student_id):
    return db.execute(
        '''
        SELECT application_id, audit_passed, gs_decision
        FROM graduation_applications
        WHERE student_id = %s
        ORDER BY application_id DESC
        LIMIT 1
        ''',
        (student_id,)
    ).fetchone()


# Load student, latest Form 1, and its courses in one call.
def load_form1_context(db, user_id):
    student = get_student_form1_context_by_user_id(db, user_id)

    latest_form1 = None
    latest_courses = []
    if student:
        latest_form1 = get_latest_form1(db, student['student_id'])
        if latest_form1:
            latest_courses = get_form1_courses_detailed(db, latest_form1['form1_id'])

    return student, latest_form1, latest_courses


# Load student, transcript, total credits, and graduation application in one call.
def load_graduation_context(db, user_id):
    student = get_student_form1_context_by_user_id(db, user_id)

    transcript_rows = []
    total_credits = 0
    graduation_application = None
    if student:
        transcript_rows = get_transcript_rows(db, student['student_id'])
        total_credits = get_total_completed_credits(db, student['student_id'])
        graduation_application = get_latest_graduation_application(db, student['student_id'])

    return student, transcript_rows, total_credits, graduation_application


# Fetch full alumni profile including program and graduation term.
def get_alumni_profile_by_user_id(db, user_id):
    return db.execute(
        '''
        SELECT
            a.alumni_id,
            a.uid,
            a.first_name,
            a.last_name,
            a.address,
            a.email,
            a.program_id,
            a.graduation_year,
            t.term_name AS graduation_term_name,
            a.final_gpa,
            u.username,
            p.program_code,
            p.program_name
        FROM alumni a
        JOIN users u ON u.user_id = a.user_id
        JOIN programs p ON p.program_id = a.program_id
        JOIN terms t ON t.term_id = a.graduation_term_id
        WHERE a.user_id = %s
        ''',
        (user_id,)
    ).fetchone()


# Fetch profile fields needed for the alumni profile edit form.
def get_editable_alumni_profile(db, user_id):
    return db.execute(
        '''
        SELECT
            a.alumni_id,
            a.uid,
            a.first_name,
            a.last_name,
            a.address,
            a.email,
            u.username,
            p.program_code,
            p.program_name
        FROM alumni a
        JOIN users u ON u.user_id = a.user_id
        JOIN programs p ON p.program_id = a.program_id
        WHERE a.user_id = %s
        ''',
        (user_id,)
    ).fetchone()


# Update editable personal fields on an alumni record.
def update_alumni_personal_info(db, alumni_id, first_name, last_name, address, email):
    db.execute(
        '''
        UPDATE alumni
        SET first_name = %s,
            last_name = %s,
            address = %s,
            email = %s
        WHERE alumni_id = %s
        ''',
        (first_name, last_name, address or None, email or None, alumni_id)
    )


# Return the student_id for a given user, or None if not found.
def get_student_id_by_user_id(db, user_id):
    row = db.execute(
        '''
        SELECT student_id
        FROM students
        WHERE user_id = %s
        ''',
        (user_id,)
    ).fetchone()
    return row['student_id'] if row else None
