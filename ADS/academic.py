# Calculate cumulative GPA; returns None (not 0.0) when no graded enrollments exist.
def calculate_gpa(db, student_id):
    gpa_row = db.execute(
        '''
        SELECT ROUND(
            SUM(c.credit_hours * g.grade_points) /
            NULLIF(SUM(c.credit_hours), 0),
            2
        ) AS gpa
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
        ''',
        (student_id,)
    ).fetchone()
    return gpa_row['gpa'] if gpa_row else None


# Count enrollments graded below B, excluding in-progress courses.
def count_grades_below_b(db, student_id):
    row = db.execute(
        '''
        SELECT COALESCE(COUNT(*), 0) AS count_below_b
        FROM student_enrollments se
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
          AND g.grade_points < 3.0
        ''',
        (student_id,)
    ).fetchone()
    return row['count_below_b'] if row else 0


# Return True if the student has three or more grades below B.
def is_on_academic_suspension(db, student_id):
    return count_grades_below_b(db, student_id) >= 3


# Count distinct completed non-CS courses.
def count_non_cs_courses(db, student_id):
    row = db.execute(
        '''
        SELECT COUNT(DISTINCT se.course_id) AS non_cs_count
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN departments d ON d.department_id = c.department_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
          AND UPPER(d.department_code) <> 'CSCI'
        ''',
        (student_id,)
    ).fetchone()
    return row['non_cs_count'] if row else 0


# Sum completed CS department credit hours.
def count_cs_credits(db, student_id):
    row = db.execute(
        '''
        SELECT COALESCE(SUM(c.credit_hours), 0) AS cs_credits
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN departments d ON d.department_id = c.department_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
          AND UPPER(d.department_code) = 'CSCI'
        ''',
        (student_id,)
    ).fetchone()
    return row['cs_credits'] if row else 0


# Return True if the student has taken all program-required courses.
def has_all_required_courses(db, student_id, program_type):
    required_rows = db.execute(
        '''
        SELECT prc.course_id
        FROM program_required_courses prc
        JOIN programs p ON p.program_id = prc.program_id
        WHERE UPPER(p.program_code) = UPPER(%s)
        ''',
        (program_type,)
    ).fetchall()

    if not required_rows:
        return True

    taken_course_rows = db.execute(
        '''
        SELECT DISTINCT se.course_id
        FROM student_enrollments se
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
        ''',
        (student_id,)
    ).fetchall()

    required_ids = {row['course_id'] for row in required_rows}
    taken_ids = {row['course_id'] for row in taken_course_rows}
    return required_ids.issubset(taken_ids)


# Return True if the student satisfies all graduation requirements for their program.
def check_graduation_requirements(db, student_id, program_type):
    requirement = db.execute(
        '''
        SELECT
            pr.min_gpa,
            pr.min_total_credits,
            pr.max_non_cs_courses,
            pr.max_grade_below_b
        FROM program_requirement pr
        JOIN programs p ON p.program_id = pr.program_id
        WHERE UPPER(p.program_code) = UPPER(%s)
        ''',
        (program_type,)
    ).fetchone()

    if not requirement:
        return False

    total_credits_row = db.execute(
        '''
        SELECT COALESCE(SUM(c.credit_hours), 0) AS total_credits
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
          AND g.grade_code <> 'IP'
        ''',
        (student_id,)
    ).fetchone()
    total_credits = total_credits_row['total_credits'] if total_credits_row else 0

    gpa = calculate_gpa(db, student_id)
    grades_below_b = count_grades_below_b(db, student_id)

    if gpa is None or gpa < requirement['min_gpa']:
        return False
    if total_credits < requirement['min_total_credits']:
        return False
    if grades_below_b > requirement['max_grade_below_b']:
        return False

    normalized_program = (program_type or '').strip().upper()
    if normalized_program == 'MS':
        if count_non_cs_courses(db, student_id) > requirement['max_non_cs_courses']:
            return False
        if not has_all_required_courses(db, student_id, program_type):
            return False
    elif normalized_program == 'PHD':
        if count_cs_credits(db, student_id) < 30:
            return False
    else:
        return False

    return True


# Sum credit hours for all non-in-progress enrollments.
def get_total_completed_credits(db, student_id):
    row = db.execute(
        '''
        SELECT
            COALESCE(SUM(CASE WHEN g.grade_code <> 'IP' THEN c.credit_hours ELSE 0 END), 0) AS total_credits
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
        ''',
        (student_id,)
    ).fetchone()
    return row['total_credits'] if row else 0


# Return GPA, credit totals, below-B count, and suspension status in one query.
def get_academic_overview(db, student_id):
    row = db.execute(
        '''
        SELECT
            ROUND(
                SUM(CASE WHEN g.grade_code <> 'IP' THEN c.credit_hours * g.grade_points ELSE 0 END) /
                NULLIF(SUM(CASE WHEN g.grade_code <> 'IP' THEN c.credit_hours ELSE 0 END), 0),
                2
            ) AS gpa,
            COALESCE(SUM(CASE WHEN g.grade_code <> 'IP' THEN c.credit_hours ELSE 0 END), 0) AS total_credits,
            COALESCE(SUM(CASE WHEN g.grade_code <> 'IP' AND g.grade_points < 3.0 THEN 1 ELSE 0 END), 0) AS grades_below_b_count
        FROM student_enrollments se
        JOIN courses c ON c.course_id = se.course_id
        JOIN grades g ON g.grade_id = se.grade_id
        WHERE se.student_id = %s
        ''',
        (student_id,)
    ).fetchone()
    grades_below_b_count = int(row['grades_below_b_count']) if row and row['grades_below_b_count'] is not None else 0
    return {
        'gpa': row['gpa'] if row else None,
        'total_credits': row['total_credits'] if row and row['total_credits'] is not None else 0,
        'grades_below_b_count': grades_below_b_count,
        'suspension_active': grades_below_b_count >= 3,
    }
