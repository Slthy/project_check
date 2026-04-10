from flask import Blueprint, render_template, request, redirect, url_for, flash
import pymysql
from auth import role_required, Role
from db import get_db
from academic import calculate_gpa
from queries import get_transcript_rows

gs_bp = Blueprint('gs', __name__, url_prefix='/gs')


# Show the graduate-secretary home page.
@gs_bp.route('/dashboard')
@role_required(Role.GS)
def gs_dashboard():
    return render_template('grad_secretary/gs_dashboard.html')


# Assign or unassign advisors to students.
@gs_bp.route('/assign-advisor', methods=['GET', 'POST'])
@role_required(Role.GS)
def assign_advisor():
    db = get_db()

    if request.method == 'POST':
        action = request.form.get('action', '').strip()
        student_id_raw = request.form.get('student_id', '').strip()

        try:
            student_id = int(student_id_raw)
        except ValueError:
            flash('Invalid student selected.', 'error')
            return redirect(url_for('gs.assign_advisor'))

        if action == 'assign':
            advisor_id_raw = request.form.get('advisor_faculty_id', '').strip()
            try:
                advisor_faculty_id = int(advisor_id_raw)
            except ValueError:
                flash('Invalid advisor selected.', 'error')
                return redirect(url_for('gs.assign_advisor'))

            advisor_row = db.execute(
                '''
                SELECT f.faculty_id
                FROM faculty f
                JOIN users u ON u.user_id = f.user_id
                WHERE f.faculty_id = %s
                  AND u.role_id = 3
                ''',
                (advisor_faculty_id,)
            ).fetchone()
            if not advisor_row:
                flash('Invalid advisor selected.', 'error')
                return redirect(url_for('gs.assign_advisor'))

            try:
                db.execute(
                    'UPDATE students SET faculty_id = %s WHERE student_id = %s',
                    (advisor_faculty_id, student_id)
                )
                db.commit()
            except pymysql.IntegrityError:
                db.rollback()
                flash('Invalid advisor selected.', 'error')
                return redirect(url_for('gs.assign_advisor'))

            flash('Advisor was assigned successfully.', 'success')
            return redirect(url_for('gs.assign_advisor'))
        elif action == 'unassign':
            db.execute(
                'UPDATE students SET faculty_id = NULL WHERE student_id = %s',
                (student_id,)
            )
            db.commit()
            flash('Advisor was unassigned successfully.', 'success')
            return redirect(url_for('gs.assign_advisor'))
        else:
            flash('Unknown action.', 'error')
            return redirect(url_for('gs.assign_advisor'))

    advisors = db.execute(
        '''
        SELECT f.faculty_id, f.first_name, f.last_name, u.username
        FROM faculty f
        JOIN users u ON u.user_id = f.user_id
        WHERE u.role_id = 3
        ORDER BY f.last_name, f.first_name
        '''
    ).fetchall()

    students = db.execute(
        '''
        SELECT
            s.student_id,
            s.uid,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name,
            s.faculty_id AS advisor_faculty_id,
            af.first_name AS advisor_first_name,
            af.last_name AS advisor_last_name,
            au.username AS advisor_username
        FROM students s
        JOIN users su ON su.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        LEFT JOIN faculty af ON af.faculty_id = s.faculty_id
        LEFT JOIN users au ON au.user_id = af.user_id
        WHERE su.role_id = 4
        ORDER BY s.last_name, s.first_name
        LIMIT 200
        '''
    ).fetchall()

    return render_template(
        'grad_secretary/assign_advisor.html',
        students=students,
        advisors=advisors
    )


# List graduation applications ready for GS decision.
@gs_bp.route('/approve-graduation')
@role_required(Role.GS)
def approve_graduation():
    applications = get_db().execute(
        '''
        SELECT
            ga.application_id,
            ga.student_id,
            ga.gs_decision,
            s.uid,
            s.first_name,
            s.last_name,
            p.program_code,
            p.program_name
        FROM graduation_applications ga
        JOIN (
            SELECT student_id, MAX(application_id) AS latest_application_id
            FROM graduation_applications
            GROUP BY student_id
        ) latest ON latest.latest_application_id = ga.application_id
        JOIN students s ON s.student_id = ga.student_id
        JOIN users su ON su.user_id = s.user_id
        JOIN programs p ON p.program_id = s.program_id
        WHERE ga.audit_passed = 1
          AND su.role_id = 4
        ORDER BY s.last_name, s.first_name
        LIMIT 200
        '''
    ).fetchall()

    return render_template(
        'grad_secretary/approve_graduation.html',
        applications=applications
    )


# Review one graduation application and apply a decision.
@gs_bp.route('/review-graduation/<int:student_id>', methods=['GET', 'POST'])
@role_required(Role.GS)
def review_graduation_application(student_id):
    db = get_db()

    application = db.execute(
        '''
        SELECT application_id, student_id, form1_id, audit_passed, gs_decision
        FROM graduation_applications
        WHERE student_id = %s
        ORDER BY application_id DESC
        LIMIT 1
        ''',
        (student_id,)
    ).fetchone()

    if request.method == 'POST':
        action = request.form.get('action', '').strip().lower()
        if not application or application['audit_passed'] != 1:
            flash('No cleared graduation application found for this student.', 'error')
            return redirect(url_for('gs.approve_graduation'))

        current_decision = (application['gs_decision'] or 'pending').strip().lower()
        if current_decision != 'pending':
            flash('This application has already been reviewed and cannot be changed.', 'error')
            return redirect(url_for('gs.review_graduation_application', student_id=student_id))

        if action == 'approve':
            try:
                student = db.execute(
                    '''
                    SELECT
                        s.student_id,
                        s.user_id,
                        s.uid,
                        s.first_name,
                        s.last_name,
                        s.address,
                        s.email,
                        s.program_id
                    FROM students s
                    WHERE s.student_id = %s
                    ''',
                    (student_id,)
                ).fetchone()
                if not student:
                    raise ValueError('Student record was not found.')

                alumni_role = db.execute(
                    "SELECT role_id FROM roles WHERE role_name = 'alumni'"
                ).fetchone()
                if not alumni_role:
                    raise ValueError('Alumni role is not configured.')

                grad_term_row = db.execute(
                    '''
                    SELECT se.term_id, se.year_taken
                    FROM student_enrollments se
                    JOIN grades g ON g.grade_id = se.grade_id
                    WHERE se.student_id = %s
                      AND g.grade_code <> 'IP'
                    ORDER BY se.year_taken DESC, se.term_id DESC
                    LIMIT 1
                    ''',
                    (student_id,)
                ).fetchone()
                if not grad_term_row:
                    raise ValueError('Cannot graduate student without completed transcript courses.')

                final_gpa = calculate_gpa(db, student_id)
                if final_gpa is None:
                    raise ValueError('Cannot compute final GPA for this student.')

                db.execute(
                    '''
                    UPDATE graduation_applications
                    SET gs_decision = 'approved'
                    WHERE application_id = %s
                    ''',
                    (application['application_id'],)
                )

                existing_alumni = db.execute(
                    '''
                    SELECT alumni_id, user_id
                    FROM alumni
                    WHERE user_id = %s OR uid = %s
                    LIMIT 1
                    ''',
                    (student['user_id'], student['uid'])
                ).fetchone()

                if existing_alumni and existing_alumni['user_id'] != student['user_id']:
                    raise ValueError('An alumni record already exists with the same UID for a different user.')

                if existing_alumni:
                    db.execute(
                        '''
                        UPDATE alumni
                        SET uid = %s,
                            first_name = %s,
                            last_name = %s,
                            address = %s,
                            email = %s,
                            program_id = %s,
                            graduation_term_id = %s,
                            graduation_year = %s,
                            final_gpa = %s
                        WHERE alumni_id = %s
                        ''',
                        (
                            student['uid'],
                            student['first_name'],
                            student['last_name'],
                            student['address'],
                            student['email'],
                            student['program_id'],
                            grad_term_row['term_id'],
                            grad_term_row['year_taken'],
                            final_gpa,
                            existing_alumni['alumni_id']
                        )
                    )
                else:
                    db.execute(
                        '''
                        INSERT INTO alumni (
                            user_id,
                            uid,
                            first_name,
                            last_name,
                            address,
                            email,
                            program_id,
                            graduation_term_id,
                            graduation_year,
                            final_gpa
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        (
                            student['user_id'],
                            student['uid'],
                            student['first_name'],
                            student['last_name'],
                            student['address'],
                            student['email'],
                            student['program_id'],
                            grad_term_row['term_id'],
                            grad_term_row['year_taken'],
                            final_gpa
                        )
                    )

                db.execute(
                    '''
                    UPDATE users
                    SET role_id = %s
                    WHERE user_id = %s
                    ''',
                    (alumni_role['role_id'], student['user_id'])
                )
                db.commit()
            except ValueError as e:
                db.rollback()
                flash(str(e), 'error')
                return redirect(url_for('gs.review_graduation_application', student_id=student_id))
            except Exception:
                db.rollback()
                flash('Failed to approve graduation. No changes were saved.', 'error')
                return redirect(url_for('gs.review_graduation_application', student_id=student_id))

            flash('Graduation application was approved successfully. Student was converted to alumni.', 'success')
            return redirect(url_for('gs.review_graduation_application', student_id=student_id))

        if action == 'reject':
            db.execute(
                '''
                UPDATE graduation_applications
                SET gs_decision = 'rejected'
                WHERE application_id = %s
                ''',
                (application['application_id'],)
            )
            db.commit()
            flash('Graduation application was rejected successfully.', 'success')
            return redirect(url_for('gs.review_graduation_application', student_id=student_id))

        flash('Unknown action.', 'error')
        return redirect(url_for('gs.review_graduation_application', student_id=student_id))

    student = db.execute(
        '''
        SELECT s.student_id, s.uid, s.first_name, s.last_name, p.program_code, p.program_name
        FROM students s
        JOIN programs p ON p.program_id = s.program_id
        WHERE s.student_id = %s
        ''',
        (student_id,)
    ).fetchone()

    transcript_rows = get_transcript_rows(db, student_id)

    form1_courses = []
    if application:
        form1_courses = db.execute(
            '''
            SELECT d.department_code, c.course_number, c.title, c.credit_hours
            FROM form1_courses fc
            JOIN courses c ON c.course_id = fc.course_id
            JOIN departments d ON d.department_id = c.department_id
            WHERE fc.form1_id = %s
            ORDER BY d.department_code, c.course_number
            ''',
            (application['form1_id'],)
        ).fetchall()

    return render_template(
        'grad_secretary/review_graduation_application.html',
        student=student,
        application=application,
        transcript_rows=transcript_rows,
        form1_courses=form1_courses
    )
