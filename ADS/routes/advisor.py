from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from auth import role_required, Role
from db import get_db
from academic import get_academic_overview
from queries import get_form_label, get_transcript_rows

advisor_bp = Blueprint('advisor', __name__, url_prefix='/advisor')


# Check whether all prerequisites for a course have been completed by a student.
def check_prerequisites(db, student_id, course_id):

    prerequisites = db.execute(
        '''
        SELECT cp.prerequisite_course_id as course_id,
               d.department_code, c.course_number, c.title
        FROM course_prerequisites cp
        JOIN courses c ON c.course_id = cp.prerequisite_course_id
        JOIN departments d ON d.department_id = c.department_id
        WHERE cp.course_id = %s
        ''',
        (course_id,)
    ).fetchall()

    result = {
        'has_prerequisites': len(prerequisites) > 0,
        'all_met': True,
        'prerequisite_details': []
    }

    for prereq in prerequisites:
        enrollment = db.execute(
            '''
            SELECT se.grade_id, g.grade_code, g.grade_points
            FROM student_enrollments se
            JOIN grades g ON g.grade_id = se.grade_id
            WHERE se.student_id = %s AND se.course_id = %s
            ''',
            (student_id, prereq['course_id'])
        ).fetchone()

        prereq_detail = {
            'course': f"{prereq['department_code']} {prereq['course_number']}",
            'title': prereq['title'],
            'completed': enrollment is not None,
            'grade': enrollment['grade_code'] if enrollment else None,
            'passed': enrollment is not None and enrollment['grade_points'] >= 2.0
        }

        result['prerequisite_details'].append(prereq_detail)

        if not prereq_detail['passed']:
            result['all_met'] = False

    return result


# Return the faculty_id for the currently logged-in advisor user.
def get_faculty_id(db):
    faculty = db.execute(
        'SELECT faculty_id FROM faculty WHERE user_id = %s',
        (session['user_id'],)
    ).fetchone()
    return faculty['faculty_id'] if faculty else None


# Show the advisor home page.
@advisor_bp.route('/dashboard')
@role_required(Role.ADVISOR)
def advisor_dashboard():
    return render_template('advisor/advisor_dashboard.html')


# List students assigned to the advisor.
@advisor_bp.route('/student_list')
@role_required(Role.ADVISOR)
def student_list():
    db = get_db()
    faculty_id = get_faculty_id(db)
    if not faculty_id:
        return render_template('advisor/student_list.html', students=[])

    students = db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name,
            COALESCE(
                SUM(
                    CASE
                        WHEN g.grade_code <> 'IP' AND g.grade_points < 3.0 THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS grades_below_b_count
        FROM students s
        JOIN users su ON su.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        LEFT JOIN student_enrollments se ON se.student_id = s.student_id
        LEFT JOIN grades g ON g.grade_id = se.grade_id
        WHERE s.faculty_id = %s
          AND su.role_id = 4
        GROUP BY
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name
        ORDER BY s.last_name, s.first_name
        LIMIT 200
        ''',
        (faculty_id,)
    ).fetchall()

    return render_template('advisor/student_list.html', students=students)


# List advisees whose latest Form 1 is ready for review.
@advisor_bp.route('/review-form1')
@role_required(Role.ADVISOR)
def review_form1_list():
    db = get_db()
    faculty_id = get_faculty_id(db)
    if not faculty_id:
        return render_template('advisor/review_form1_list.html', students=[])

    students = db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name,
            COALESCE(f1.advisor_decision, 'pending') AS review_status
        FROM students s
        JOIN users su ON su.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        JOIN form1 f1 ON f1.form1_id = (
            SELECT f1_latest.form1_id
            FROM form1 f1_latest
            WHERE f1_latest.student_id = s.student_id
            ORDER BY f1_latest.form1_id DESC
            LIMIT 1
        )
        WHERE s.faculty_id = %s
          AND su.role_id = 4
          AND f1.audit_passed = 1
        ORDER BY s.last_name, s.first_name
        ''',
        (faculty_id,)
    ).fetchall()

    return render_template('advisor/review_form1_list.html', students=students)


# Show one advisee profile and transcript summary.
@advisor_bp.route('/student/<int:student_id>')
@role_required(Role.ADVISOR)
def advisor_student_detail(student_id):
    db = get_db()
    faculty_id = get_faculty_id(db)
    if not faculty_id:
        return redirect(url_for('advisor.advisor_dashboard'))

    student = db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            s.address,
            s.email,
            p.program_code,
            p.program_name
        FROM students s
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.student_id = %s
          AND s.faculty_id = %s
        ''',
        (student_id, faculty_id)
    ).fetchone()

    if not student:
        return redirect(url_for('advisor.student_list'))

    transcript_rows = get_transcript_rows(db, student_id)
    overview = get_academic_overview(db, student_id)

    return render_template(
        'advisor/student_detail.html',
        student=student,
        transcript_rows=transcript_rows,
        gpa=overview['gpa'],
        total_credits=overview['total_credits'],
        grades_below_b_count=overview['grades_below_b_count'],
        suspension_active=overview['suspension_active']
    )


# Review and approve/reject the latest Form 1 for an advisee.
@advisor_bp.route('/review-form1/<int:student_id>', methods=['GET', 'POST'])
@role_required(Role.ADVISOR)
def review_form1(student_id):
    db = get_db()
    faculty_id = get_faculty_id(db)
    if not faculty_id:
        return redirect(url_for('advisor.advisor_dashboard'))

    if request.method == 'POST':
        action = request.form.get('action')

        student = db.execute(
            '''
            SELECT s.student_id, p.program_code
            FROM students s
            JOIN programs p ON p.program_id = s.program_id
            WHERE s.student_id = %s AND s.faculty_id = %s
            ''',
            (student_id, faculty_id)
        ).fetchone()
        if not student:
            flash('You can only review Form 1 for your own advisees.', 'error')
            return redirect(url_for('advisor.student_list'))
        form_label = get_form_label(student['program_code'])

        form1 = db.execute(
            'SELECT form1_id, audit_passed FROM form1 WHERE student_id = %s ORDER BY form1_id DESC LIMIT 1',
            (student_id,)
        ).fetchone()

        if not form1 or form1['audit_passed'] != 1:
            flash(f'Latest {form_label} must pass audit before review.', 'error')
            return redirect(url_for('advisor.review_form1_list'))

        if action == 'reject':
            db.execute(
                '''
                UPDATE form1
                SET advisor_decision = 'rejected'
                WHERE form1_id = %s
                ''',
                (form1['form1_id'],)
            )
            db.commit()
            flash(f'{form_label} was rejected successfully.', 'success')
        elif action == 'approve':
            db.execute(
                '''
                UPDATE form1
                SET advisor_decision = 'approved'
                WHERE form1_id = %s
                ''',
                (form1['form1_id'],)
            )
            db.commit()
            flash(f'{form_label} was approved successfully.', 'success')
        else:
            flash('Unknown action.', 'error')

        return redirect(url_for('advisor.review_form1_list'))

    student = db.execute(
        '''
        SELECT s.student_id, s.uid, s.first_name, s.last_name,
               p.program_code, p.program_name
        FROM students s
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.student_id = %s
          AND s.faculty_id = %s
        ''',
        (student_id, faculty_id)
    ).fetchone()

    if not student:
        flash('You can only access your own advisees.', 'error')
        return redirect(url_for('advisor.student_list'))
    form_label = get_form_label(student['program_code'])

    form1 = db.execute(
        'SELECT form1_id, student_id, audit_passed, advisor_decision AS review_status FROM form1 WHERE student_id = %s ORDER BY form1_id DESC LIMIT 1',
        (student_id,)
    ).fetchone()

    if not form1 or form1['audit_passed'] != 1:
        flash(f'Latest {form_label} must pass audit before review.', 'error')
        return redirect(url_for('advisor.review_form1_list'))

    courses = []
    course_rows = db.execute(
        '''
        SELECT c.course_id, d.department_code, c.course_number, c.title, c.credit_hours
        FROM form1_courses fc
        JOIN courses c ON c.course_id = fc.course_id
        JOIN departments d ON d.department_id = c.department_id
        WHERE fc.form1_id = %s
        ''',
        (form1['form1_id'],)
    ).fetchall()

    for course_row in course_rows:
        course_dict = dict(course_row)
        course_dict['prerequisite_validation'] = check_prerequisites(db, student_id, course_dict['course_id'])
        courses.append(course_dict)

    return render_template(
        'advisor/review_form1.html',
        student=student,
        form1=form1,
        courses=courses,
        form_label=form_label
    )
