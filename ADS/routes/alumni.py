from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from auth import role_required, Role
from db import get_db
from academic import get_academic_overview
from queries import (
    get_alumni_profile_by_user_id,
    get_editable_alumni_profile,
    get_student_id_by_user_id,
    get_transcript_rows,
    is_valid_email,
    update_alumni_personal_info,
)

alumni_bp = Blueprint('alumni', __name__, url_prefix='/alumni')


# Show the alumni home page.
@alumni_bp.route('/dashboard')
@role_required(Role.ALUMNI)
def alumni_dashboard():
    return render_template('alumni/alumni_dashboard.html')


# Show alumni profile details.
@alumni_bp.route('/profile')
@role_required(Role.ALUMNI)
def alumni_profile():
    alumni = get_alumni_profile_by_user_id(get_db(), session['user_id'])
    return render_template('alumni/alumni_profile.html', alumni=alumni)


# Edit alumni personal info.
@alumni_bp.route('/profile/edit', methods=['GET', 'POST'])
@role_required(Role.ALUMNI)
def edit_alumni_profile():
    db = get_db()
    alumni = get_editable_alumni_profile(db, session['user_id'])
    if not alumni:
        flash('No alumni profile was found for this account.', 'error')
        return render_template('alumni/edit_alumni_profile.html', alumni=None)

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
            update_alumni_personal_info(
                db,
                alumni['alumni_id'],
                first_name,
                last_name,
                address,
                email
            )
            db.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('alumni.alumni_profile'))

        alumni = get_editable_alumni_profile(db, session['user_id'])

    return render_template('alumni/edit_alumni_profile.html', alumni=alumni)


# Show the alumni transcript view.
@alumni_bp.route('/transcript')
@role_required(Role.ALUMNI)
def alumni_transcript():
    db = get_db()
    alumni = get_alumni_profile_by_user_id(db, session['user_id'])
    student_id = get_student_id_by_user_id(db, session['user_id'])

    transcript_rows = []
    overview = None
    if student_id:
        transcript_rows = get_transcript_rows(db, student_id)
        overview = get_academic_overview(db, student_id)

    return render_template(
        'alumni/alumni_transcript.html',
        alumni=alumni,
        transcript_rows=transcript_rows,
        total_credits=overview['total_credits'] if overview else 0,
        gpa=overview['gpa'] if overview else None
    )
