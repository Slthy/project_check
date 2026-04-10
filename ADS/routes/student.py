from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
import pymysql
from auth import role_required, Role
from db import get_db
from fpdf import FPDF
from itertools import groupby
from academic import check_graduation_requirements, get_academic_overview
from queries import (
    get_editable_student_profile,
    get_form1_course_ids,
    get_form_label,
    get_latest_form1,
    get_latest_graduation_application,
    get_student_form1_context_by_user_id,
    get_student_profile_with_advisor_by_user_id,
    get_transcript_course_ids,
    get_transcript_rows,
    is_valid_email,
    load_form1_context,
    load_graduation_context,
)

student_bp = Blueprint('student', __name__, url_prefix='/student')


# Return the form label appropriate for the student's program.
def get_student_form_label(student):
    return get_form_label(student['program_code']) if student else 'Form 1'


# Render the Form 1 page with all required template context.
def render_form1_page(student, latest_form1, latest_courses, form_label, overview, audit_issues):
    return render_template(
        'student/form1.html',
        student=student,
        latest_form1=latest_form1,
        latest_courses=latest_courses,
        audit_issues=audit_issues,
        form_label=form_label,
        grades_below_b_count=overview['grades_below_b_count'] if overview else 0,
        suspension_active=overview['suspension_active'] if overview else False
    )


# Show the student dashboard.
@student_bp.route('/dashboard')
@role_required(Role.STUDENT)
def student_dashboard():
    db = get_db()
    student = db.execute(
        '''
        SELECT s.student_id, p.program_code
        FROM students s
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.user_id = %s
        ''',
        (session['user_id'],)
    ).fetchone()

    grades_below_b_count = 0
    suspension_active = False
    if student:
        overview = get_academic_overview(db, student['student_id'])
        grades_below_b_count = overview['grades_below_b_count']
        suspension_active = overview['suspension_active']

    return render_template(
        'student/student_dashboard.html',
        suspension_active=suspension_active,
        grades_below_b_count=grades_below_b_count
    )


# Show the student profile.
@student_bp.route('/profile')
@role_required(Role.STUDENT)
def student_profile():
    student = get_student_profile_with_advisor_by_user_id(get_db(), session['user_id'])
    return render_template('student/student_profile.html', student=student)


# Edit student profile fields.
@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@role_required(Role.STUDENT)
def edit_student_profile():
    db = get_db()
    student = get_editable_student_profile(db, session['user_id'])

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        address = request.form.get('address', '').strip()
        email = request.form.get('email', '').strip()

        if not first_name or not last_name:
            flash('First name and last name are required.', 'error')
        elif not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
        else:
            db.execute(
                '''
                UPDATE students
                SET first_name = %s,
                    last_name = %s,
                    address = %s,
                    email = %s
                WHERE student_id = %s
                ''',
                (
                    first_name,
                    last_name,
                    address or None,
                    email or None,
                    student['student_id']
                )
            )
            db.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('student.student_profile'))

        student = get_editable_student_profile(db, session['user_id'])

    return render_template('student/edit_student_profile.html', student=student)


# Show the transcript with summary stats.
@student_bp.route('/transcript')
@role_required(Role.STUDENT)
def view_transcript():
    db = get_db()
    student = get_student_profile_with_advisor_by_user_id(db, session['user_id'])
    transcript_rows = get_transcript_rows(db, student['student_id'])
    overview = get_academic_overview(db, student['student_id'])

    return render_template(
        'student/student_transcript.html',
        student=student,
        transcript_rows=transcript_rows,
        gpa=overview['gpa'],
        total_credits=overview['total_credits'],
        grades_below_b_count=overview['grades_below_b_count'],
        suspension_active=overview['suspension_active']
    )


@student_bp.route('/transcript/download')
@role_required(Role.STUDENT)
def download_transcript():
    db = get_db()
    student = get_student_profile_with_advisor_by_user_id(db, session['user_id'])
    transcript_rows = get_transcript_rows(db, student['student_id'])
    overview = get_academic_overview(db, student['student_id'])

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # Header
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'George Washington University', ln=True, align='C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, 'Unofficial Academic Transcript', ln=True, align='C')
    pdf.ln(6)

    # Divider
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # Student info
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Name:', ln=False)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, f"{student['first_name']} {student['last_name']}", ln=True)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'UID:', ln=False)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, student['uid'], ln=True)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Program:', ln=False)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, student.get('program_name', student['program_code']), ln=True)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(40, 7, 'Email:', ln=False)
    pdf.set_font('Helvetica', '', 11)
    pdf.cell(0, 7, student.get('email') or 'N/A', ln=True)
    pdf.ln(4)

    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    # Group rows by year + term
    def term_sort_key(row):
        term_order = {'Fall': 1, 'Spring': 2, 'Summer': 3}
        return (row['year_taken'], term_order.get(row['term_name'], 99))

    sorted_rows = sorted(transcript_rows, key=term_sort_key)
    grouped = groupby(sorted_rows, key=lambda r: (r['year_taken'], r['term_name']))

    for (year, term), courses in grouped:
        courses = list(courses)

        # Term header
        pdf.set_font('Helvetica', 'B', 11)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(0, 8, f'{term} {year}', ln=True, fill=True)
        pdf.ln(1)

        # Column headers
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(30, 7, 'Course', border='B')
        pdf.cell(90, 7, 'Title', border='B')
        pdf.cell(20, 7, 'Credits', border='B', align='C')
        pdf.cell(20, 7, 'Grade', border='B', align='C')
        pdf.ln()

        # Course rows
        pdf.set_font('Helvetica', '', 10)
        term_points = 0
        term_credits = 0
        for course in courses:
            course_code = f"{course['department_code']} {course['course_number']}"
            pdf.cell(30, 7, course_code)
            pdf.cell(90, 7, course['title'])
            pdf.cell(20, 7, str(course['credit_hours']), align='C')
            pdf.cell(20, 7, course['grade_code'], align='C')
            pdf.ln()

            # Accumulate for term GPA
            if course['grade_code'] != 'IP':
                term_points += course['grade_points'] * course['credit_hours']
                term_credits += course['credit_hours']

        # Term GPA
        if term_credits > 0:
            term_gpa = term_points / term_credits
            pdf.set_font('Helvetica', 'I', 10)
            pdf.cell(0, 7, f'Term GPA: {term_gpa:.2f}', align='R')
            pdf.ln()

    # GPA summary
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)
    pdf.set_font('Helvetica', 'B', 11)
    gpa_text = f"Cumulative GPA: {overview['gpa']:.2f}" if overview['gpa'] else 'Cumulative GPA: N/A'
    pdf.cell(80, 7, gpa_text)
    pdf.cell(60, 7, f"Total Credits: {overview['total_credits']}")
    pdf.ln()

    response = make_response(bytes(pdf.output()))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=transcript_{student["uid"]}.pdf'
    return response


# Show the latest Form 1 submission.
@student_bp.route('/form1')
@role_required(Role.STUDENT)
def form1():
    db = get_db()
    student, latest_form1, latest_courses = load_form1_context(db, session['user_id'])
    form_label = get_student_form_label(student)
    overview = get_academic_overview(db, student['student_id']) if student else None
    return render_form1_page(student, latest_form1, latest_courses, form_label, overview, [])


# Run audit checks for the latest Form 1.
@student_bp.route('/form1/audit')
@role_required(Role.STUDENT)
def audit_form1():
    db = get_db()
    student, latest_form1, latest_courses = load_form1_context(db, session['user_id'])
    form_label = get_student_form_label(student)
    overview = get_academic_overview(db, student['student_id']) if student else None
    suspension_active = overview['suspension_active'] if overview else False

    if suspension_active:
        suspension_message = 'You are under academic suspension (3 or more grades below B).'
        flash(f'{form_label} audit is unavailable while on academic suspension.', 'error')
        return render_form1_page(
            student, latest_form1, latest_courses, form_label, overview, [suspension_message]
        )

    if not latest_form1:
        flash(f'No {form_label} found. Create a {form_label} before running an audit.', 'error')
        return render_form1_page(
            student,
            latest_form1,
            latest_courses,
            form_label,
            overview,
            [f'No latest {form_label} submission was found.']
        )

    requirement = db.execute(
        '''
        SELECT min_total_credits, max_non_cs_credits
        FROM program_requirement
        WHERE program_id = %s
        ''',
        (student['program_id'],)
    ).fetchone()

    audit_issues = []
    selected_course_ids = {course['course_id'] for course in latest_courses}
    total_credits = sum(course['credit_hours'] for course in latest_courses)
    non_cs_credits = sum(
        course['credit_hours']
        for course in latest_courses
        if (course['department_code'] or '').strip().upper() != 'CSCI'
    )
    max_non_cs_credits = requirement['max_non_cs_credits']

    if total_credits < requirement['min_total_credits']:
        audit_issues.append('Total credits are below the minimum (30).')

    if non_cs_credits > max_non_cs_credits:
        audit_issues.append('Total non-CS credits exceed the maximum (6).')

    required_courses = db.execute(
        '''
        SELECT
            prc.course_id,
            d.department_code,
            c.course_number
        FROM program_required_courses prc
        JOIN courses c ON c.course_id = prc.course_id
        JOIN departments d ON d.department_id = c.department_id
        WHERE prc.program_id = %s
        ORDER BY d.department_code, c.course_number
        ''',
        (student['program_id'],)
    ).fetchall()

    if required_courses and any(
        course['course_id'] not in selected_course_ids
        for course in required_courses
    ):
        audit_issues.append('One or more required courses are missing.')

    if selected_course_ids:
        selected_course_id_list = sorted(selected_course_ids)
        placeholders = ','.join(['%s'] * len(selected_course_id_list))
        prerequisite_rows = db.execute(
            f'''
            SELECT
                cp.prerequisite_course_id
            FROM course_prerequisites cp
            WHERE cp.course_id IN ({placeholders})
            ''',
            selected_course_id_list
        ).fetchall()

        if any(
            row['prerequisite_course_id'] not in selected_course_ids
            for row in prerequisite_rows
        ):
            audit_issues.append('One or more selected courses are missing prerequisites.')

    audit_passed = 0
    if audit_issues:
        flash(f'{form_label} audit failed. See issues below.', 'error')
    else:
        flash(f'{form_label} audit passed. Your latest {form_label} meets program requirements.', 'success')
        audit_passed = 1

    db.execute(
        '''
        UPDATE form1
        SET audit_passed = %s
        WHERE form1_id = %s
        ''',
        (audit_passed, latest_form1['form1_id'])
    )
    db.commit()

    latest_form1 = db.execute(
        '''
        SELECT form1_id, student_id, audit_passed, advisor_decision AS review_status
        FROM form1
        WHERE form1_id = %s
        ''',
        (latest_form1['form1_id'],)
    ).fetchone()

    return render_form1_page(
        student, latest_form1, latest_courses, form_label, overview, audit_issues
    )


# Create or edit a Form 1 submission.
@student_bp.route('/form1/edit', methods=['GET', 'POST'])
@role_required(Role.STUDENT)
def edit_form1():
    db = get_db()
    student = get_student_form1_context_by_user_id(db, session['user_id'])
    form_label = get_student_form_label(student)
    suspension_active = get_academic_overview(db, student['student_id'])['suspension_active'] if student else False

    if suspension_active:
        flash(f'{form_label} editing is unavailable while on academic suspension.', 'error')
        return redirect(url_for('student.form1'))

    available_courses = db.execute(
        '''
        SELECT
            c.course_id,
            d.department_code,
            c.course_number,
            c.title,
            c.credit_hours
        FROM courses c
        JOIN departments d ON d.department_id = c.department_id
        ORDER BY d.department_code, c.course_number
        '''
    ).fetchall()

    transcript_course_ids = get_transcript_course_ids(db, student['student_id'])

    selected_course_ids = list(dict.fromkeys(transcript_course_ids))

    latest_form1 = get_latest_form1(db, student['student_id'])

    if latest_form1:
        latest_form1_course_ids = get_form1_course_ids(db, latest_form1['form1_id'])
        selected_course_ids = list(
            dict.fromkeys(transcript_course_ids + latest_form1_course_ids)
        )

    def render_edit_page(selected_ids):
        return render_template(
            'student/form1_edit.html',
            student=student,
            available_courses=available_courses,
            selected_course_ids=selected_ids,
            transcript_course_ids=transcript_course_ids,
            latest_form1=latest_form1,
            form_label=form_label
        )

    if request.method == 'POST':
        submitted_course_ids = request.form.getlist('course_ids')
        try:
            parsed_ids = [int(value) for value in submitted_course_ids]
        except ValueError:
            flash('Invalid course selection.', 'error')
            return render_edit_page(submitted_course_ids)

        available_course_ids = {course['course_id'] for course in available_courses}
        invalid_course_ids = [
            course_id for course_id in parsed_ids
            if course_id not in available_course_ids
        ]
        if invalid_course_ids:
            flash('Invalid course selection.', 'error')
            return render_edit_page(list(dict.fromkeys(transcript_course_ids + parsed_ids)))

        unique_ids = list(dict.fromkeys(transcript_course_ids + parsed_ids))

        if not unique_ids:
            flash('Please select at least one course.', 'error')
        elif len(unique_ids) > 12:
            flash(f'{form_label} allows at most 12 courses including transcript courses.', 'error')
        else:
            try:
                if latest_form1:
                    form1_id = latest_form1['form1_id']
                    db.execute(
                        '''
                        UPDATE form1
                        SET audit_passed = -1, advisor_decision = 'pending'
                        WHERE form1_id = %s
                        ''',
                        (form1_id,)
                    )
                    db.execute(
                        'DELETE FROM form1_courses WHERE form1_id = %s',
                        (form1_id,)
                    )
                else:
                    insert_form1_cursor = db.execute(
                        "INSERT INTO form1 (student_id, audit_passed, advisor_decision) VALUES (%s, -1, 'pending')",
                        (student['student_id'],)
                    )
                    form1_id = insert_form1_cursor.lastrowid

                db.executemany(
                    'INSERT INTO form1_courses (form1_id, course_id) VALUES (%s, %s)',
                    [(form1_id, course_id) for course_id in unique_ids]
                )
                db.commit()
            except pymysql.IntegrityError:
                db.rollback()
                flash('Invalid course selection.', 'error')
                return render_edit_page(unique_ids)
            except Exception:
                db.rollback()
                flash('An unexpected error occurred. Please try again.', 'error')
                return render_edit_page(unique_ids)

            flash(f'{form_label} was submitted successfully.', 'success')
            return redirect(url_for('student.form1'))

    return render_edit_page(selected_course_ids)


# Show graduation application status and context.
@student_bp.route('/apply-graduation')
@role_required(Role.STUDENT)
def apply_graduation():
    db = get_db()
    student, transcript_rows, total_credits, graduation_application = load_graduation_context(db, session['user_id'])
    overview = get_academic_overview(db, student['student_id']) if student else None

    return render_template(
        'student/apply_graduation.html',
        student=student,
        transcript_rows=transcript_rows,
        gpa=overview['gpa'] if overview else None,
        total_credits=total_credits,
        graduation_application=graduation_application,
        audit_issues=[],
        grades_below_b_count=overview['grades_below_b_count'] if overview else 0,
        suspension_active=overview['suspension_active'] if overview else False
    )


# Audit graduation readiness and submit application.
@student_bp.route('/apply-graduation/audit')
@role_required(Role.STUDENT)
def audit_graduation_application():
    db = get_db()
    student, transcript_rows, total_credits, graduation_application = load_graduation_context(db, session['user_id'])

    latest_form1 = get_latest_form1(db, student['student_id'])

    requirement = db.execute(
        '''
        SELECT min_gpa, max_grade_below_b
        FROM program_requirement pr
        JOIN programs p ON p.program_id = pr.program_id
        WHERE pr.program_id = %s
        ''',
        (student['program_id'],)
    ).fetchone()

    overview = get_academic_overview(db, student['student_id'])
    gpa = overview['gpa']
    grades_below_b_count = overview['grades_below_b_count']
    suspension_active = overview['suspension_active']
    audit_issues = []
    program_type = (student['program_code'] or '').strip().upper()
    form_label = get_form_label(program_type)

    if suspension_active:
        audit_issues.append('Student is under academic suspension (3 or more grades below B).')

    if not latest_form1:
        audit_issues.append(f'No {form_label} found.')
    elif (latest_form1['review_status'] or '').strip().lower() != 'approved':
        audit_issues.append(f'{form_label} is not approved by advisor.')

    transcript_course_ids = set(get_transcript_course_ids(db, student['student_id']))

    form1_course_ids = set()
    if latest_form1:
        form1_course_ids = set(get_form1_course_ids(db, latest_form1['form1_id']))

    if latest_form1 and transcript_course_ids != form1_course_ids:
        audit_issues.append(f'Transcript courses do not match {form_label}.')

    if gpa is None or gpa < requirement['min_gpa']:
        audit_issues.append(f'GPA is below minimum ({requirement["min_gpa"]:.2f}).')

    if grades_below_b_count > requirement['max_grade_below_b']:
        audit_issues.append(
            f'Grades below B must be no more than {requirement["max_grade_below_b"]}.'
        )

    if not check_graduation_requirements(db, student['student_id'], program_type):
        if program_type == 'MS':
            audit_issues.append('Graduation requirements for the MS program are not met.')
        elif program_type == 'PHD':
            audit_issues.append('Graduation requirements for the PhD program are not met.')

    audit_passed = 0 if audit_issues else 1

    if latest_form1 and audit_passed == 1:
        existing_application = db.execute(
            '''
            SELECT application_id, gs_decision
            FROM graduation_applications
            WHERE student_id = %s
            ORDER BY application_id DESC
            LIMIT 1
            ''',
            (student['student_id'],)
        ).fetchone()

        latest_decision = ''
        if existing_application and existing_application['gs_decision']:
            latest_decision = existing_application['gs_decision'].strip().lower()

        if existing_application and latest_decision in ('', 'pending'):
            db.execute(
                '''
                UPDATE graduation_applications
                SET form1_id = %s, audit_passed = 1, gs_decision = 'pending'
                WHERE application_id = %s
                ''',
                (latest_form1['form1_id'], existing_application['application_id'])
            )
        else:
            db.execute(
                '''
                INSERT INTO graduation_applications (student_id, form1_id, audit_passed, gs_decision)
                VALUES (%s, %s, 1, 'pending')
                ''',
                (student['student_id'], latest_form1['form1_id'])
            )
        db.commit()
        graduation_application = get_latest_graduation_application(db, student['student_id'])

    if audit_issues:
        flash('Graduation application audit failed. See issues below.', 'error')
    else:
        flash('Graduation application audit passed.', 'success')

    return render_template(
        'student/apply_graduation.html',
        student=student,
        transcript_rows=transcript_rows,
        gpa=gpa,
        total_credits=total_credits,
        graduation_application=graduation_application,
        audit_issues=audit_issues,
        grades_below_b_count=grades_below_b_count,
        suspension_active=suspension_active
    )
