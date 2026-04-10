from pathlib import Path

from flask import Blueprint, session, render_template, redirect, url_for, request, flash, g
from flask_session import Session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, uuid, mysql.connector,re,random,uuid6

APPS_DIR = Path(__file__).resolve().parent
apps_bp = Blueprint(
    'apps',
    __name__,
    template_folder=str(APPS_DIR / 'templates'),
    static_folder=str(APPS_DIR / 'static'),
)

DATABASE = str(APPS_DIR / 'appsdb.db')
SCHEMA_PATH = APPS_DIR / 'APPS_Schema.sql'

def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@apps_bp.teardown_app_request
def close_db(error):
    db = getattr(g, '_db', None)
    if db is not None:
        db.close()

def init_db():
    if not os.path.exists(DATABASE):
        db = sqlite3.connect(DATABASE)
        with open(SCHEMA_PATH, encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
        db.close()
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    users = db.execute('SELECT user_id, password FROM users').fetchall()
    for u in users:
        p = u['password']
        if p and not p.startswith('pbkdf2:') and not p.startswith('scrypt:'):
            db.execute('UPDATE users SET password=? WHERE user_id=?',
                       [generate_password_hash(p), u['user_id']])
    db.commit()
    db.close()
init_db()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('Please log in first.')
            return redirect(url_for('apps.login'))
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user' not in session or session['user']['role'] not in roles:
                flash('You are not authorized to access this page.')
                return redirect(url_for('apps.home_page'))
            return f(*args, **kwargs)
        return decorated
    return decorator

def generate_prefixed_id(prefix):
    return f"{prefix}{uuid6.uuid7().hex[:8]}"

def generate_uid():
    db = get_db()

    last_applicant = db.execute("SELECT uid FROM applicants WHERE uid GLOB '[0-9]*' ORDER BY CAST(uid AS INTEGER) DESC LIMIT 1").fetchone()

    if last_applicant and last_applicant['uid']:
        next_num = int(last_applicant['uid']) + 1
    else:
        next_num = 1

    return str(next_num).zfill(8)

def update_application_completeness(app_id):
    db = get_db()
    application = db.execute('SELECT * FROM applications WHERE app_id=?',[app_id]).fetchone()

    if not application:
        return False

    transcript = db.execute('SELECT * FROM transcripts WHERE app_id=?',[app_id]).fetchone()

    recommendation = db.execute('''SELECT * FROM recommendation
           WHERE app_id=? AND submitted=1 LIMIT 1''',[app_id]).fetchone()

    has_transcript = bool(transcript and transcript['received'])
    has_recommendation = bool(recommendation)

    if has_transcript and has_recommendation:
        if application['status'] == 'Incomplete':
            db.execute("UPDATE applications SET status='Complete' WHERE app_id=?",[app_id])
        return True

    if application['status'] == 'Complete':
        db.execute("UPDATE applications SET status='Incomplete' WHERE app_id=?",[app_id])

    return False

def parse_gre_score(value, low, high):
    """Return int if value is a valid integer in [low, high], else None."""
    try:
        v = int(value)
        return v if low <= v <= high else None
    except (TypeError, ValueError):
        return None

def generate_prefixed_id(prefix):
   return f"{prefix}-{uuid6.uuid7()}"

@apps_bp.route('/')
def home_page():
    return render_template("homepage.html")

@apps_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE user_id=?',[username]).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user'] = {'username': user['user_id'],'role': user['role_id'],'email': user['email']}
            flash('You have logged in successfully', 'Success')
            role_id = user['role_id']
            if role_id == 0:
                return redirect(url_for('apps.applicant'))
            elif role_id == 1:
                return redirect(url_for('apps.student'))
            elif role_id == 2:
                return redirect(url_for('apps.faculty'))
            elif role_id == 3:
                return redirect(url_for('apps.gs'))
            elif role_id == 4:
                return redirect(url_for('apps.cac_home'))
            elif role_id == 5:
                return redirect(url_for('apps.admin'))
            else:
                flash('Invalid role', 'error')
                return redirect(url_for('apps.login'))
        else:
            flash('Username or password is incorrect', 'Failure')
    return render_template('login.html')

@apps_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('apps.home_page'))

@apps_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        if not all([email, password, username, confirm_password]):
            flash('All fields are required', 'failure')
        elif confirm_password != password:
            flash('Please make sure you enter the same password')
        else:
            db = get_db()
            if db.execute('SELECT email FROM users WHERE email=?', [email]).fetchone():
                flash('This email already exists, please try a different one')
            elif db.execute('SELECT user_id FROM users WHERE user_id=?', [username]).fetchone():
                flash('This username already exists, please use a different one')
            else:
                db.execute('INSERT INTO users (user_id,email,password,role_id) VALUES(?,?,?,?)',
                           [username, email, generate_password_hash(password), 0])
                db.commit()
                session['user'] = {'username': username,'role': 0,'email': email}
                flash('Account created successfully', 'Success')
                return redirect(url_for('apps.applicant'))
    return render_template('signup.html')

@apps_bp.route('/applicant/application', methods=['GET', 'POST'])
@login_required
@role_required(0)
def application():
    username = session['user']['username']
    if request.method == 'POST':
        db = get_db()
        fname   = request.form.get('fname', '').strip()
        lname   = request.form.get('lname', '').strip()
        ssn = request.form.get('ssn', '').strip()
        student_number = request.form.get('student_number', '').strip()
        if student_number and not re.fullmatch(r'\d{8}', student_number):
            flash('Student Number must be exactly 8 digits.')
            departments = db.execute('SELECT * FROM departments').fetchall()
            programs    = db.execute('SELECT * FROM programs').fetchall()
            return render_template('application.html', departments=departments, programs=programs)
        if not re.fullmatch(r'\d{9}', ssn):
            flash('SSN must be exactly 9 digits.')
            departments = db.execute('SELECT * FROM departments').fetchall()
            programs    = db.execute('SELECT * FROM programs').fetchall()
            return render_template('application.html', departments=departments, programs=programs)
        ssn_hashed = generate_password_hash(ssn)
        dob     = request.form.get('dob', '')
        address = request.form.get('address', '').strip()
        if not all([fname, lname, ssn, dob, address]):
            flash('Some personal information fields are missing.')
            departments = db.execute('SELECT * FROM departments').fetchall()
            programs    = db.execute('SELECT * FROM programs').fetchall()
            return render_template('application.html', departments=departments, programs=programs)
        existing_applicant = db.execute('SELECT uid FROM applicants WHERE user_id=?', [username]).fetchone()
        if existing_applicant:
            uid = existing_applicant['uid']
            db.execute(
                'UPDATE applicants SET fname=?,lname=?,address=?,dob=?,ssn=? WHERE uid=?',
                [fname, lname, address, dob, ssn_hashed, uid]
            )
        else:
            uid = generate_uid()
            db.execute(
                'INSERT INTO applicants (uid,user_id,fname,lname,address,dob,ssn) VALUES(?,?,?,?,?,?,?)',
                [uid, username, fname, lname, address, dob, ssn]
            )
        aid = generate_prefixed_id("A")
        # Academic Information
        toefl_score = request.form.get('toefl_score', '').strip()
        toefl_exam_date = request.form.get('toefl_exam_date', '').strip()
        areas_of_interest = request.form.get('areas_of_interest', '').strip()
        experience_summary = request.form.get('experience_summary', '').strip()

        deg_no = request.form.get('deg_no', '')

        verbal = parse_gre_score(request.form.get('verbal', ''), 130, 170)
        quantitative = parse_gre_score(request.form.get('quantitative', ''), 130, 170)

        if deg_no == '2' and not (verbal and quantitative):   # '2' = PhD
            flash('GRE Verbal and Quantitative scores are required for PhD applicants.')
            departments = db.execute('SELECT * FROM departments').fetchall()
            programs    = db.execute('SELECT * FROM programs').fetchall()
            return render_template('application.html', departments=departments, programs=programs)
        pnumber  = request.form.get('pnumber', '')
        semester = request.form.get('semester', '')
        app_year = request.form.get('app_year', '')
        if not all([deg_no, pnumber, semester, app_year]):
            flash('Some academic information fields are missing.')
            return render_template('application.html')
        db.execute('''INSERT INTO applications (app_id, uid, deg_no, pro_no, semester, app_year, status, 
                   toefl_score, toefl_exam_year, areas_of_interest) VALUES(?,?,?,?,?,?,?,?,?,?)''', [
                               aid, uid, deg_no, pnumber, semester, app_year, 'Incomplete',
                               int(toefl_score) if toefl_score else None,
                               toefl_exam_date[:4] if toefl_exam_date else None,
                               areas_of_interest or None])
        db.commit()
        # Work Experience — multiple entries
        job_titles   = request.form.getlist('job_title[]')
        descriptions = request.form.getlist('description[]')
        com_names    = request.form.getlist('com_name[]')
        man_names    = request.form.getlist('man_name[]')
        man_emails   = request.form.getlist('man_email[]')
        man_numbers  = request.form.getlist('man_number[]')
        start_dates  = request.form.getlist('start_date[]')
        end_dates    = request.form.getlist('end_date[]')
        for job_title, description, com_name, man_name, man_email, man_number, start_date, end_date in zip(
                job_titles, descriptions, com_names, man_names, man_emails, man_numbers, start_dates, end_dates):
            if job_title.strip():
                wid = generate_prefixed_id('W')
                db.execute(
                    'INSERT INTO workex (wid,app_id,job_title,description,com_name,man_name,man_email,man_number,start_date,end_date) VALUES(?,?,?,?,?,?,?,?,?,?)',
                    [wid, aid, job_title.strip(), description, com_name, man_name.strip(), man_email.strip(), man_number, start_date or None, end_date or None]
                )
        db.commit()
        # Previous Degrees 
        dtypes  = request.form.getlist('dtype[]')
        dyears  = request.form.getlist('dyear[]')
        dunis   = request.form.getlist('duni[]')
        dmajors = request.form.getlist('dmajor[]')
        dgpas   = request.form.getlist('dGPA[]')
        for dtype, dyear, duni, dmajor, dgpa in zip(dtypes, dyears, dunis, dmajors, dgpas):
            if dtype and duni:
                try:
                    gpa_val = float(dgpa) if dgpa else None
                    if gpa_val is not None and not (0.0 <= gpa_val <= 4.0):
                        flash(f'GPA must be between 0.00 and 4.00 (got {dgpa}).')
                        departments = db.execute('SELECT * FROM departments').fetchall()
                        programs = db.execute('SELECT * FROM programs').fetchall()
                        return render_template('application.html', departments=departments, programs=programs)

                except ValueError:
                    flash('GPA must be a number between 0.00 and 4.00.')
                    departments = db.execute('SELECT * FROM departments').fetchall()
                    programs = db.execute('SELECT * FROM programs').fetchall()
                    return render_template('application.html', departments=departments, programs=programs)

                deg_id = generate_prefixed_id('D')
                db.execute(
                    'INSERT INTO previous_deg (deg_id,app_id,dtype,dyear,dGPA,duni,dmajor) VALUES(?,?,?,?,?,?,?)',
                    [deg_id, aid, dtype, dyear or None, gpa_val, duni, dmajor])
                db.commit()
        # Recommendation 
        rfname = request.form.get('rfname', '').strip()
        rlname = request.form.get('rlname', '').strip()
        remail = request.form.get('remail', '').strip()
        rnumber = request.form.get('rnumber', '').strip()
        raffiliation = request.form.get('raffiliation', '').strip()
        rtitle = request.form.get('rtitle', '').strip()

        last_rid = None
        if rfname and rlname and remail and raffiliation and rtitle:
            last_rid = generate_prefixed_id('R')
            db.execute(
                'INSERT INTO recommendation (rid,app_id,rfname,rlname,remail,rnumber,raffiliation,rtitle,submitted) VALUES(?,?,?,?,?,?,?,?,?)',
                [last_rid, aid, rfname, rlname, remail, rnumber, raffiliation, rtitle, False]
            )
            db.commit()
        else:
            flash('One recommendation request is required.')
            departments = db.execute('SELECT * FROM departments').fetchall()
            programs = db.execute('SELECT * FROM programs').fetchall()
            return render_template('application.html', departments=departments, programs=programs)
        # Transcript
        transcript = request.form.get('transcript', 'false')
        sent_date  = request.form.get('sent_date', '') or None
        trans_id   = generate_prefixed_id('T')
        db.execute(
            'INSERT INTO transcripts (trans_id,app_id,received,received_date) VALUES(?,?,?,?)',
            [trans_id, aid, False, sent_date]
        )
        db.commit()
        # GRE Scores 
        verbal       = parse_gre_score(request.form.get('verbal', ''), 130, 170)
        quantitative = parse_gre_score(request.form.get('quantitative', ''), 130, 170)
        gre_total    = (verbal + quantitative) if (verbal and quantitative) else None
        subj_score   = parse_gre_score(request.form.get('subj_score', ''), 200, 990)
        exam_year    = parse_gre_score(request.form.get('exam_year', ''), 2015, 2026)
        subj_name    = request.form.get('subj_name', '').strip() or None
        gid = generate_prefixed_id('G')
        db.execute(
            'INSERT INTO gre (gid,app_id,verbal,quantitative,total,subj_score,subj_name,exam_year) VALUES(?,?,?,?,?,?,?,?)',
            [gid, aid, verbal, quantitative, gre_total, subj_score, subj_name, exam_year]
        )

        update_application_completeness(aid)

        db.commit()
        flash('Application submitted successfully!', 'Success')

        if last_rid:
            return redirect(url_for('apps.recommendation_request_email', rid=last_rid))
        return redirect(url_for('apps.applicant'))
    db = get_db()
    departments = db.execute('SELECT * FROM departments').fetchall()
    programs = db.execute('SELECT * FROM programs').fetchall()
    return render_template('application.html', departments=departments, programs=programs)

@apps_bp.route('/applicant/recommendation-request/<rid>')
@login_required
@role_required(0)
def recommendation_request_email(rid):
    db = get_db()
    username = session['user']['username']

    applicant_rec = db.execute('SELECT * FROM applicants WHERE user_id=?',[username]).fetchone()

    if not applicant_rec:
        flash('Applicant record not found')
        return redirect(url_for('apps.applicant'))
    
    rec = db.execute('''SELECT recommendation.* FROM recommendation
           JOIN applications ON recommendation.app_id = applications.app_id
           WHERE recommendation.rid=? AND applications.uid=?''',
        [rid, applicant_rec['uid']]).fetchone()

    if not rec:
        flash('Recommendation request not found')
        return redirect(url_for('apps.applicant'))

    submission_link = url_for('apps.recommendation_submit', rid=rid, _external=True)

    return render_template('recommendation_request_email.html',rec=rec,submission_link=submission_link)

@apps_bp.route('/programs')
def programs():
    return render_template('programs.html')

# Role 0 — Applicant homepage (can apply and check status)
@apps_bp.route('/applicant')
@login_required
@role_required(0)
def applicant():
    db = get_db()
    username = session['user']['username']

    applicant_rec = db.execute(
        'SELECT * FROM applicants WHERE user_id=?',
        [username]
    ).fetchone()

    app_data = None
    student_account = None

    if applicant_rec:
        app_data = db.execute(
            'SELECT * FROM applications WHERE uid=?',
            [applicant_rec['uid']]
        ).fetchone()

        student_account = db.execute(
            '''SELECT users.user_id
               FROM students
               JOIN users ON students.user_id = users.user_id
               WHERE students.uid=?''',
            [applicant_rec['uid']]
        ).fetchone()

    return render_template(
        'applicant.html',
        app_data=app_data,
        student_account=student_account
    )

@apps_bp.route('/applicant/status')
@login_required
@role_required(0)
def status():
    db = get_db()
    username = session['user']['username']

    applicant_rec = db.execute('SELECT * FROM applicants WHERE user_id=?',[username]).fetchone()

    app_data = None
    transcript = None
    recommendations = []
    status_message = 'No application found.'

    if applicant_rec:
        app_data = db.execute('''SELECT applications.*, programs.pname, soughtdeg.deg_type
            FROM applications
            JOIN programs ON applications.pro_no = programs.pnumber
            JOIN soughtdeg ON applications.deg_no = soughtdeg.deg_no
            WHERE uid=?''', [applicant_rec['uid']]).fetchone()

    if app_data:
        transcript = db.execute('SELECT * FROM transcripts WHERE app_id=?',[app_data['app_id']]).fetchone()

        recommendations = db.execute('SELECT * FROM recommendation WHERE app_id=?',[app_data['app_id']]).fetchall()

        missing_items = []

        if not transcript or not transcript['received']:
            missing_items.append('official transcript')

        if not recommendations:
            missing_items.append('recommendation letter')
        else:
            if not any(rec['submitted'] for rec in recommendations):
                missing_items.append('recommendation letter')

        if app_data['final_dec'] == 'Reject':
            status_message = 'Your application for admission has been denied.'
        elif app_data['final_dec'] in ['Admit', 'Admit with Aid']:
            status_message = 'Congratulations you have been admitted. The formal letter of acceptance will be mailed.'
        elif missing_items or app_data['status'] == 'Incomplete':
            status_message = 'Application Incomplete - missing ' + ', '.join(missing_items) if missing_items else 'Application Incomplete'
        elif app_data['status'] in ['Complete', 'Under Review', 'Reviewed']:
            status_message = 'Application Complete and Under Review / No Decision Yet'
        elif app_data['status'] == 'Decision Made':
            if app_data['final_dec'] == 'Reject':
                status_message = 'Your application for admission has been denied.'
            else:
                status_message = 'Congratulations you have been admitted. The formal letter of acceptance will be mailed.'

    return render_template('status.html', app_data=app_data, status_message=status_message,transcript=transcript,recommendations=recommendations)

@apps_bp.route('/student')
@login_required
@role_required(1)
def student():
    db = get_db()
    username = session['user']['username']
    student_rec = db.execute('SELECT * FROM students WHERE user_id=?', [username]).fetchone()
    advisor = None
    app_data = None
    if student_rec:
        app_data = db.execute('''SELECT applications.*, programs.pname, soughtdeg.deg_type
            FROM applications
            JOIN programs ON applications.pro_no = programs.pnumber
            JOIN soughtdeg ON applications.deg_no = soughtdeg.deg_no
            WHERE applications.app_id=?''', [student_rec['admit_app_id']]).fetchone()
        advisor = db.execute('''SELECT faculty.fname, faculty.lname, faculty.user_id
            FROM review
            JOIN faculty ON review.recom_advisor_id = faculty.user_id
            WHERE review.app_id=? AND review.recom_advisor_id IS NOT NULL
            LIMIT 1''', [student_rec['admit_app_id']]).fetchone()

    return render_template('student.html', student=student_rec, advisor=advisor, app_data=app_data)

@apps_bp.route('/faculty')
@login_required
@role_required(2)
def faculty():
    return render_template('faculty.html')

@apps_bp.route('/faculty/recommendations')
@login_required
@role_required(2,4)
def recommendation_list():
    db = get_db()
    username = session['user']['username']
    user = db.execute('SELECT user_id, role_id FROM users WHERE user_id=?', [username]).fetchone()

    if user and user['role_id'] == 4:
        recommendations = db.execute('SELECT * FROM recommendation ORDER BY rid').fetchall()
    
    else:
        recommendations = db.execute("""SELECT DISTINCT recommendation.* FROM recommendation
        JOIN review ON recommendation.app_id = review.app_id
        WHERE review.reviewer_id = ? ORDER BY recommendation.rid""", [username]).fetchall()

    role = 'CAC' if user and user['role_id'] == 4 else 'Faculty'
    return render_template('recommendation_list.html', recommendations=recommendations, role=role)

@apps_bp.route('/recommendation/<rid>', methods=['GET','POST'])
def recommendation_submit(rid):
    db = get_db()

    rec = db.execute('SELECT * FROM recommendation WHERE rid = ?', [rid]).fetchone()

    if not rec:
        flash('Recommendation request not found')
        return redirect(url_for('apps.home_page'))
    
    if rec['submitted']:
        return render_template('recommendation_submitted.html', rec=rec)
    
    if request.method == 'POST':
        letter_text = request.form.get('recommendation','').strip()

        if not letter_text:
            flash('Recommendation Letter cannot be empty')
            return render_template('recommendations.html', rec = rec)
    
        db.execute("""UPDATE recommendation SET letter_text=?, submitted=TRUE, submitted_date=DATE('now') WHERE rid=?""", [letter_text, rid])

        update_application_completeness(rec['app_id'])

        db.commit()

        return render_template('recommendation_submitted.html', rec=rec)
    
    return render_template('recommendations.html', rec=rec)

@apps_bp.route('/gs')
@login_required
@role_required(3)
def gs():
    db = get_db()

    transcript_pending_apps = db.execute("""SELECT applications.*, applicants.fname, applicants.lname,transcripts.received, transcripts.received_date
        FROM applications
        JOIN applicants ON applications.uid = applicants.uid
        LEFT JOIN transcripts ON applications.app_id = transcripts.app_id
        WHERE transcripts.received IS NULL OR transcripts.received = 0
        ORDER BY applications.app_id""").fetchall()

    ready_apps = db.execute("""SELECT * FROM applications
        JOIN applicants ON applications.uid = applicants.uid
        WHERE status = 'Complete' ORDER BY applications.app_id""").fetchall()

    under_review_apps = db.execute("""SELECT * FROM applications
        JOIN applicants ON applications.uid = applicants.uid
        WHERE status = 'Under Review' ORDER BY applications.app_id""").fetchall()

    dec_ready_apps = db.execute("""SELECT * FROM applications
        JOIN applicants ON applications.uid = applicants.uid
        WHERE status = 'Reviewed' ORDER BY applications.app_id """).fetchall()

    return render_template('gs.html',transcript_pending_apps=transcript_pending_apps,ready_apps=ready_apps,under_review_apps=under_review_apps,dec_ready_apps=dec_ready_apps)

@apps_bp.route('/gs/transcript/<app_id>/receive', methods=['POST'])
@login_required
@role_required(3)
def mark_transcript_received(app_id):
    db = get_db()
    application = db.execute('SELECT * FROM applications WHERE app_id=?',[app_id]).fetchone()

    if not application:
        flash('Application not found')
        return redirect(url_for('apps.gs'))

    transcript = db.execute('SELECT * FROM transcripts WHERE app_id=?',[app_id]).fetchone()

    if not transcript:
        flash('Transcript record not found for this application')
        return redirect(url_for('apps.gs'))

    if transcript['received']:
        flash('Transcript has already been marked as received')
        return redirect(url_for('apps.gs'))

    db.execute("UPDATE transcripts SET received=1, received_date=DATE('now') WHERE app_id=?", [app_id])

    update_application_completeness(app_id)

    db.commit()
    flash('Transcript marked as received successfully')
    return redirect(url_for('apps.gs'))

@apps_bp.route('/dashboard/cac_gs')
@login_required
@role_required(3, 4)
def cac_gs_dashboard():
    db = get_db()
    username = session['user']['username']

    user = db.execute('SELECT user_id, role_id FROM users WHERE user_id=?',[username]).fetchone()

    applications = db.execute("""SELECT * FROM applications JOIN applicants ON applications.uid = applicants.uid 
        JOIN soughtdeg ON applications.deg_no = soughtdeg.deg_no 
        JOIN programs ON pro_no = pnumber WHERE status IN ('Complete', 'Under Review', 'Reviewed', 'Decision Made') ORDER BY app_id """).fetchall()

    reviewers = []
    if user['role_id'] == 4:
        reviewers = db.execute(""" SELECT a.user_id, a.fname, a.lname,
            d.dname FROM Faculty a
            JOIN Departments d ON a.dno = d.dnumber
            JOIN users u ON a.user_id = u.user_id
            WHERE u.role_id IN (2, 4)
            ORDER BY a.user_id """).fetchall()

    role = 'CAC' if user['role_id'] == 4 else 'GS'

    return render_template( 'cac_gs_dashboard.html', applications=applications, reviewers=reviewers, role =role)

@apps_bp.route('/dashboard/cac_gs/application/<app_id>')
@login_required
@role_required(3, 4)
def view_application(app_id):
    db = get_db()
    username = session['user']['username']

    user = db.execute('SELECT user_id, role_id FROM users WHERE user_id=?',[username]).fetchone()

    application = db.execute(""" 
        SELECT * FROM applications 
        JOIN applicants ON applications.uid = applicants.uid
        WHERE applications.app_id = ? 
    """, [app_id]).fetchone()

    if not application:
        return "Application not found", 404
    
    gre = db.execute("SELECT * FROM gre WHERE app_id = ?", [app_id]).fetchone()
    previous_degs = db.execute("SELECT * FROM previous_deg WHERE app_id = ?", [app_id]).fetchall()
    work_experience = db.execute("SELECT * FROM workex WHERE app_id = ?", [app_id]).fetchall()
    recommendations = db.execute("SELECT * FROM recommendation WHERE app_id = ?", [app_id]).fetchall()

    return render_template('view_application.html', application=application, gre=gre,
        previous_degs=previous_degs,
        work_experience=work_experience,
        recommendations=recommendations)


@apps_bp.route('/reviews/assigned', methods=['GET'])
@login_required
@role_required(2, 4)
def assigned_reviews():
    db = get_db()
    username = session['user']['username']

    assigned_apps = db.execute(""" SELECT * FROM review
        JOIN applications ON review.app_id = applications.app_id
        JOIN applicants ON applications.uid = applicants.uid
        WHERE review.reviewer_id = ? AND applications.status IN ('Complete', 'Under Review') 
        ORDER BY applications.app_id""", [username]).fetchall()

    completed_apps = db.execute("""SELECT * FROM review
        JOIN applications ON review.app_id = applications.app_id
        JOIN applicants ON applications.uid = applicants.uid
        WHERE review.reviewer_id = ? AND applications.status IN ('Reviewed', 'Decision Made')
        ORDER BY applications.app_id""", [username]).fetchall()

    return render_template('reviewapp.html', assigned_apps=assigned_apps , completed_apps=completed_apps)


@apps_bp.route('/createacc', methods=['GET', 'POST'])
@login_required
@role_required(5)
def create_acc():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password','')
        confirm_password = request.form.get('confirm_password','')
        role = request.form.get('role')

        if confirm_password != password:
            flash('Passwords do not match', 'failure')
        elif not all([email, password, username, confirm_password, role]):
            flash('All Fields are required', 'failure')
        else:
            db = get_db()
            if db.execute('SELECT email FROM users WHERE email=?', [email]).fetchone():
                flash('This email already exists', 'failure')
            elif db.execute('SELECT user_id FROM users WHERE user_id=?', [username]).fetchone():
                flash('This username already exists')
            else:
                db.execute('INSERT INTO users (user_id, email, password, role_id) VALUES (?,?,?,?)',
                [username, email, generate_password_hash(password), role])
                db.commit()
                flash('Account created successfully', 'success')
                return redirect(url_for('apps.admin'))
    return render_template('createacc.html')

@apps_bp.route('/admin')
@login_required
@role_required(5)
def admin():
    return render_template('admin.html')

@apps_bp.route('/dashboard/cac_gs/assign_reviewers', methods=['POST'])
@login_required
@role_required(4)
def assign_reviewers():
    db = get_db()
    username = session['user']['username']
    user = db.execute('SELECT user_id, role_id FROM users WHERE user_id=?', [username]).fetchone()

    if not user or user['role_id'] != 4:
        return "Unauthorized", 403

    application_id = request.form.get('application_id')
    reviewer_ids = request.form.getlist('reviewer_id')

    if not application_id or not reviewer_ids:
        flash('You must choose at least one reviewer')
        return redirect(url_for('apps.cac_gs_dashboard'))

    application = db.execute('SELECT * FROM applications WHERE app_id=?',[application_id]).fetchone()

    if not application:
        flash('Application not found')
        return redirect(url_for('apps.cac_gs_dashboard'))

    if application['status'] != 'Complete':
        flash('Reviewers have already been assigned for this application')
        return redirect(url_for('apps.cac_gs_dashboard'))

    existing_reviews = db.execute('SELECT * FROM review WHERE app_id=?',[application_id]).fetchall()

    if existing_reviews:
        flash('Reviewers have already been assigned for this application')
        return redirect(url_for('apps.cac_gs_dashboard'))

    for reviewer_id in reviewer_ids:
        reviewer = db.execute('SELECT * FROM faculty JOIN users ON faculty.user_id = users.user_id WHERE faculty.user_id=? AND role_id IN (2, 4)',
        [reviewer_id]).fetchone()

        if not reviewer:
            flash('One of the reviewers is invalid')
            return redirect(url_for('apps.cac_gs_dashboard'))

    last_review = db.execute("SELECT review_id FROM review ORDER BY review_id DESC LIMIT 1").fetchone()

    if last_review:
        next_id_num = int(last_review['review_id'].replace('REV', '')) + 1
    else:
        next_id_num = 1

    for reviewer_id in reviewer_ids:
        review_id = f"REV{str(next_id_num).zfill(3)}"
        db.execute('INSERT INTO review (review_id, app_id, reviewer_id) VALUES (?, ?, ?)',
        [review_id, application_id, reviewer_id])

        next_id_num += 1

    db.execute("UPDATE applications SET status = 'Under Review' WHERE app_id=?",[application_id])

    db.commit()
    flash('Reviewers assigned successfully')
    return redirect(url_for('apps.cac_gs_dashboard'))

@apps_bp.route('/cac')
@login_required
@role_required(4)
def cac_home():
    if 'user' not in session:
        return redirect(url_for('apps.login'))
    db = get_db()

    ready_apps = db.execute("SELECT * FROM applications JOIN applicants ON applications.uid = applicants.uid WHERE status = 'Complete' ").fetchall()

    under_review_apps = db.execute("SELECT * FROM applications JOIN applicants ON applications.uid = applicants.uid WHERE status = 'Under Review'").fetchall()

    dec_ready_apps = db.execute("SELECT * FROM applications JOIN applicants ON applications.uid = applicants.uid WHERE status = 'Reviewed'").fetchall()

    return render_template('cac.html', ready_apps=ready_apps, under_review_apps=under_review_apps,
        dec_ready_apps = dec_ready_apps)

@apps_bp.route('/reviews/<app_id>', methods=['GET','POST'])
@login_required
@role_required(2, 4)
def review_application(app_id):    
    db = get_db()
    username = session['user']['username']
    user = db.execute('SELECT user_id, role_id FROM users WHERE user_id=?', [username]).fetchone()

    application = db.execute("""SELECT * FROM applications 
        JOIN applicants ON applications.uid = applicants.uid
        JOIN soughtdeg ON applications.deg_no = soughtdeg.deg_no
        WHERE applications.app_id=?""",[app_id]).fetchone()
    if not application:
        flash('Application not found')
        return redirect(url_for('apps.assigned_reviews'))
    
    if application['status'] not in ['Complete', 'Under Review']:
        flash('This application is not ready for review.')
        return redirect(url_for('apps.assigned_reviews'))
    
    assigned_review = db.execute('SELECT * FROM review WHERE app_id=? AND reviewer_id=?',[app_id, username]).fetchone()

    if not assigned_review:
        flash('You are not assigned to review this application')
        return redirect(url_for('apps.assigned_reviews'))
    
    degrees = db.execute('SELECT * FROM previous_deg WHERE app_id=?',[app_id]).fetchall()
    gre = db.execute('SELECT * FROM gre WHERE app_id=?',[app_id]).fetchone()
    workex = db.execute('SELECT * FROM workex WHERE app_id=?',[app_id]).fetchall()
    recommendations = db.execute('SELECT * FROM recommendation WHERE app_id=?',[app_id]).fetchall()
    advisors = db.execute('SELECT * FROM faculty ORDER BY lname, fname').fetchall()

    if request.method == 'POST':
        rating = request.form.get('rating')
        recom_advisor_id = request.form.get('recom_advisor_id')
        comments = request.form.get('comments')
        reject_reason = request.form.get('reject_reason')
        deficiency_courses = request.form.get('deficiency_courses')
        
        for rec in recommendations:
            rid = rec['rid']
            letter_rating = request.form.get(f'letter_rating_{rid}')
            is_generic = request.form.get(f'is_generic_{rid}')
            is_credible = request.form.get(f'is_credible_{rid}')

            db.execute('''UPDATE recommendation SET letter_rating=?, is_generic=?, is_credible=?
               WHERE rid=?''',
            [int(letter_rating) if letter_rating else None,
                1 if is_generic == 'Y' else 0 if is_generic == 'N' else None,
                1 if is_credible == 'Y' else 0 if is_credible == 'N' else None,
                rid])

        if rating == '0' and not reject_reason:
            flash('A reject reason is required when the rating is Reject')
            return render_template('reviewapp.html',application=application,degrees=degrees,
                gre=gre,workex=workex,recommendations=recommendations,advisors=advisors,review=assigned_review)

        db.execute("""UPDATE review SET rating=?, recom_advisor_id=?, comments=?,
            reject_reason=?, deficiency_courses=?
            WHERE app_id=? AND reviewer_id=?""", [rating, recom_advisor_id, comments,
            reject_reason, deficiency_courses, app_id, username])

        incomplete_reviews = db.execute("""SELECT * FROM review WHERE app_id=?
              AND rating IS NULL""", [app_id]).fetchall()

        if not incomplete_reviews:
            db.execute("UPDATE applications SET status='Reviewed' WHERE app_id=?",[app_id])

        db.commit()
        flash('Review submitted successfully')
        return redirect(url_for('apps.assigned_reviews'))
        
    return render_template('reviewapp.html', application = application, degrees=degrees, 
    gre=gre,workex=workex,recommendations= recommendations, advisors=advisors, review=assigned_review)

@apps_bp.route('/modifyacc', methods=['GET', 'POST'])
@login_required
@role_required(5) 
def modifyacc():
    db = get_db()
    users = db.execute('''SELECT users.*, review.review_id, applications.app_id FROM users 
                       LEFT JOIN applicants ON users.user_id = applicants.user_id
                       LEFT JOIN applications ON applicants.uid = applications.uid
                       LEFT JOIN review ON applications.app_id = review.app_id''').fetchall()
    role_map = {
        0: 'Applicant',
        1: 'Student',
        2: 'Faculty Reviewer',
        3: 'GS',
        4: 'CAC',
        5: 'Admin'
    }
    return render_template('modifyacc.html', users=users, role_map = role_map)

@apps_bp.route('/modifyacc/<username>', methods=['GET', 'POST'])
@login_required
@role_required(5)
def modify_user(username):
    db = get_db()
    user = db.execute('''SELECT users.*, applications.app_id, review.review_id FROM users 
                       LEFT JOIN applicants ON users.user_id = applicants.user_id
                       LEFT JOIN applications ON applicants.uid = applications.uid
                       LEFT JOIN review ON applications.app_id = review.app_id
                       WHERE users.user_id = ?''', [username]).fetchone()
    #Okay, so problems: 
    #1. While everything else updates, reviewID and appID cannot be changed if they do not already exist
    #2. This is fine, instead I will re-code it slight
    #3. We are going to do this instead, if theres an existing application then it is editable and viewable.
    #4. If there is no existing application or reviewID, or rather both, then we can create one
    #5. this is going to need a link next to editacc.html
    #6. It will also need an if statement which is just if exists do this if not do this
    #7. Okay I cant do this until later, when applications is done

    if request.method == 'POST':
        user_name = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role_id')
        appid = request.form.get('app_id', '').strip()
        revid = request.form.get('review_id', '').strip()
        hashed_password = generate_password_hash(password) if password else user['password']
        db.execute('UPDATE users SET user_id=?, email=?, password=?, role_id=? WHERE user_id=?',[user_name, email, hashed_password, role, username])
        has_review = None
        has_app = None
        applicant = db.execute('SELECT uid FROM applicants WHERE user_id=?', [user_name]).fetchone()
        if applicant:
            uid = applicant['uid']
            # Get current app id before any changes
            existingapp = db.execute('SELECT * FROM applications WHERE uid=?', [uid]).fetchone()
            old_appid = existingapp['app_id'] if existingapp else None

            if revid and old_appid:
                existing_review = db.execute('SELECT * FROM review WHERE app_id=?', [old_appid]).fetchone()
                if not existing_review:
                    has_review = False
                else:
                    has_review = True
                    # check if new review id is taken by a SEPERATE row
                    conflict = db.execute('SELECT * FROM review WHERE review_id=? AND app_id!=?', [revid, old_appid]).fetchone()

                    if not conflict:
                        db.execute('UPDATE review SET review_id=? WHERE app_id=?', [revid, old_appid])
                    else:
                        flash('That Review ID is already in use', 'warning')
                        return redirect(url_for('apps.modify_user', username=username))

            if appid and old_appid:
                has_app = True
                if appid != old_appid:
                    #Cascade to every other table that has app_id in it, otherwise it wont edit properly
                    db.execute('UPDATE workex SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE previous_deg SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE recommendation SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE transcripts SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE gre SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE review SET app_id=? WHERE app_id=?', [appid, old_appid])
                    db.execute('UPDATE students SET admit_app_id=? WHERE admit_app_id=?', [appid, old_appid])
                    db.execute('UPDATE applications SET app_id=? WHERE uid=?', [appid, uid])
            elif appid and not old_appid:
                has_app = False
                    
        db.commit()
        warned = False
        if (appid or revid) and applicant is None:
            flash('Cannot update App/Review ID: this user has no applicant record.', 'warning')
            warned = True
        if appid and has_app is False:
            flash('Cannot update App ID: no existing application found for this user. Please create one first.', 'warning')
            warned = True
        if revid and has_review is False:
            flash('Cannot update Review ID: no existing review found for this user. Please create one first.', 'warning')
            warned = True
        if not warned:
            flash('Account updated successfully', 'success')
        return redirect(url_for('apps.modify_user', username=user_name))
    return render_template('editacc.html', user = user)



#Mostly a copy and paste of the original application with slight tweaks to make it suitable for admin
@apps_bp.route('/modifyacc/<username>/application/create', methods=['GET', 'POST'])
@login_required
@role_required(5)
def admin_create_app(username):
    db = get_db()
    applicant = db.execute('SELECT * FROM applicants WHERE user_id=?', [username]).fetchone()
    
    existing_app = None
    if applicant:
        existing_app = db.execute('SELECT * FROM applications WHERE uid=?', [applicant['uid']]).fetchone()
        if existing_app:
            flash('This user already has an application', 'warning')
            return redirect(url_for('apps.modify_user', username=username))

    if request.method == 'POST':

        uid = applicant['uid'] if applicant else generate_uid()
        aid = generate_prefixed_id("A")

        # Personal Information 
        fname   = request.form.get('fname', '').strip()
        lname   = request.form.get('lname', '').strip()
        middle  = request.form.get('middle', '').strip()
        ssn     = request.form.get('ssn', '')
        dob     = request.form.get('dob', '')
        address = request.form.get('address', '')
        toefl_score      = request.form.get('toefl_score', '') or None
        toefl_exam_year  = request.form.get('toefl_exam_year', '') or None
        areas_of_interest = request.form.get('areas_of_interest', '')

        if not all([fname, lname, ssn, dob, address]):
            flash('Some personal information fields are missing.')
            return render_template('admin_create_application.html')

        # Academic Information
        deg_no   = request.form.get('deg_no', '')
        pnumber  = request.form.get('pnumber', '')
        semester = request.form.get('semester', '')
        app_year = request.form.get('app_year', '')

        if not all([deg_no, pnumber, semester, app_year]):
            flash('Some academic information fields are missing.')
            return render_template('admin_create_application.html')
        
        if not applicant:
            db.execute(
                'INSERT INTO applicants (uid, user_id, fname, lname, address, dob, ssn) VALUES(?,?,?,?,?,?,?)',
                [uid, username, fname, lname, address, dob, ssn]
            )
            db.commit()
        else:
            db.execute(
                'UPDATE applicants SET fname=?, lname=?, address=?, dob=?, ssn=? WHERE uid=?',
                [fname, lname, address, dob, ssn, uid]
            )
            db.commit()

        db.execute(
            'INSERT INTO applications (app_id, uid, deg_no, pro_no, semester, app_year, status, toefl_score, toefl_exam_year, areas_of_interest) VALUES(?,?,?,?,?,?,?,?,?,?)',
            [aid, uid, deg_no, pnumber, semester, app_year, 'Incomplete', toefl_score, toefl_exam_year, areas_of_interest]
        )
        db.commit()

        # Work Experience 
        job_title   = request.form.get('job_title', '').strip()
        description = request.form.get('description', '')
        com_name    = request.form.get('com_name', '')
        man_name    = request.form.get('man_name', '').strip()
        man_email   = request.form.get('man_email', '').strip()
        man_number  = request.form.get('man_number', '')
        start_date  = request.form.get('start_date', '')
        end_date    = request.form.get('end_date', '')

        if job_title:
            wid = generate_prefixed_id('W')
            db.execute(
                'INSERT INTO workex (wid,app_id,job_title,description,com_name,man_name,man_email,man_number,start_date,end_date) VALUES(?,?,?,?,?,?,?,?,?,?)',
                [wid, aid, job_title, description, com_name, man_name, man_email, man_number, start_date, end_date]
            )
            db.commit()

        # Previous Degrees 
        dtypes  = request.form.getlist('dtype[]')
        dyears  = request.form.getlist('dyear[]')
        dunis   = request.form.getlist('duni[]')
        dmajors = request.form.getlist('dmajor[]')
        dgpas   = request.form.getlist('dGPA[]')

        for dtype, dyear, duni, dmajor, dgpa in zip(dtypes, dyears, dunis, dmajors, dgpas):
            if dtype and duni:  # skip blank extra degree fieldsets
                deg_id = generate_prefixed_id('D')
                db.execute(
                    'INSERT INTO previous_deg (deg_id,app_id,dtype,dyear,dGPA,duni,dmajor) VALUES(?,?,?,?,?,?,?)',
                    [deg_id, aid, dtype, dyear or None, dgpa or None, duni, dmajor]
                )
        db.commit()

        # Recommendation 
        rfname      = request.form.get('rfname', '')
        rlname      = request.form.get('rlname', '')
        remail      = request.form.get('remail', '')
        rnumber     = request.form.get('rnumber', '')
        submitted   = request.form.get('submitted', 'false')
        raffiliation = request.form.get('raffiliation', '')
        rtitle      = request.form.get('rtitle', '')

        if rfname: 
            rid = generate_prefixed_id('R')
            db.execute(
                'INSERT INTO recommendation (rid,app_id,rfname,rlname,remail,rnumber,raffiliation,rtitle,submitted) VALUES(?,?,?,?,?,?,?,?,?)',
                [rid, aid, rfname, rlname, remail, rnumber, raffiliation, rtitle, submitted == 'true']
            )
            db.commit()

        # Transcript
        transcript = request.form.get('transcript', 'false')
        sent_date  = request.form.get('sent_date', '') or None
        trans_id   = generate_prefixed_id('T')
        db.execute(
            'INSERT INTO transcripts (trans_id,app_id,received,received_date) VALUES(?,?,?,?)',
            [trans_id, aid, False, sent_date]
        )
        db.commit()

        # GRE Scores 
        verbal       = request.form.get('verbal', '') or None
        quantitative = request.form.get('quantitative', '') or None
        gre_total    = request.form.get('gre_total', '') or None
        exam_year    = request.form.get('exam_year', '') or None
        subj_score   = request.form.get('subj_score', '') or None
        subj_name    = request.form.get('subj_name', '') or None

        gid = generate_prefixed_id('G')
        db.execute(
            'INSERT INTO gre (gid,app_id,verbal,quantitative,total,subj_score,subj_name,exam_year) VALUES(?,?,?,?,?,?,?,?)',
            [gid, aid, verbal, quantitative, gre_total, subj_score, subj_name, exam_year]
        )
        update_application_completeness(aid)
        db.commit()

        flash('Application submitted successfully!', 'Success')
        return redirect(url_for('apps.modify_user', username=username))

    return render_template('admin_create_application.html', username=username)

#Differs mainly in updating over inserting. Its a lot of redundant code tbh but oh well
@apps_bp.route('/modifyacc/<username>/application/edit', methods=['GET', 'POST'])   
@login_required
@role_required(5)
def admin_edit_app(username):
    db = get_db()
    applicant = db.execute('SELECT * FROM applicants WHERE user_id=?', [username]).fetchone()
    
    if not applicant:
        flash('This user has no application', 'warning')
        return redirect(url_for('apps.modify_user', username=username))
    
    appdata = db.execute('SELECT * FROM applications WHERE uid=?', [applicant['uid']]).fetchone()
    if not appdata:
        flash('This user has no existing application', 'warning')
        return redirect(url_for('apps.modify_user', username=username))
    aid = appdata['app_id']
    degrees         = db.execute('SELECT * FROM previous_deg WHERE app_id=?', [aid]).fetchall()
    gre             = db.execute('SELECT * FROM gre WHERE app_id=?', [aid]).fetchone()
    workex          = db.execute('SELECT * FROM workex WHERE app_id=?', [aid]).fetchone()
    recommendation  = db.execute('SELECT * FROM recommendation WHERE app_id=?', [aid]).fetchone()
    transcript      = db.execute('SELECT * FROM transcripts WHERE app_id=?', [aid]).fetchone()
    program = db.execute('SELECT * FROM programs WHERE pnumber=?', [appdata['pro_no']]).fetchone()

    if request.method == 'POST':
        fname   = request.form.get('fname', '').strip()
        lname   = request.form.get('lname', '').strip()
        ssn     = request.form.get('ssn', '')
        dob     = request.form.get('dob', '')
        address = request.form.get('address', '')

        db.execute('''UPDATE applicants SET fname=?, lname=?, address=?, dob=?, ssn=?
                WHERE uid=?''', [fname, lname, address, dob, ssn, applicant['uid']])
        db.commit()

        # Academic Information
        deg_no   = request.form.get('deg_no', '')
        pnumber  = request.form.get('pnumber', '')
        semester = request.form.get('semester', '')
        app_year = request.form.get('app_year', '')
        status   = request.form.get('status', '')
        toefl_score      = request.form.get('toefl_score', '') or None
        toefl_exam_year  = request.form.get('toefl_exam_year', '') or None
        areas_of_interest = request.form.get('areas_of_interest', '')

        db.execute(
            '''UPDATE applications SET deg_no=?, pro_no=?, semester=?, app_year=?, status=?, 
            toefl_score=?, toefl_exam_year=?, areas_of_interest=? WHERE app_id=?''',
            [deg_no, pnumber, semester, app_year, status, toefl_score, toefl_exam_year, areas_of_interest, aid])
        db.commit()

        # Work Experience 
        description = request.form.get('description', '')
        job_title  = request.form.get('job_title', '').strip()
        com_name   = request.form.get('com_name', '')
        man_name   = request.form.get('man_name', '').strip()
        man_email  = request.form.get('man_email', '').strip()
        man_number = request.form.get('man_number', '')
        start_date = request.form.get('start_date', '')
        end_date   = request.form.get('end_date', '')
        if workex:
            db.execute('''UPDATE workex SET job_title=?, description=?, com_name=?, 
           man_name=?, man_email=?, man_number=?, start_date=?, end_date=?
           WHERE app_id=?''', [job_title, description, com_name, man_name, 
           man_email, man_number, start_date, end_date, aid])
        db.commit()
        db.execute('DELETE FROM previous_deg WHERE app_id=?', [aid])
        dtypes  = request.form.getlist('dtype[]')
        dyears  = request.form.getlist('dyear[]')
        dunis   = request.form.getlist('duni[]')
        dmajors = request.form.getlist('dmajor[]')
        dgpas   = request.form.getlist('dGPA[]')

        for dtype, dyear, duni, dmajor, dgpa in zip(dtypes, dyears, dunis, dmajors, dgpas):
            if dtype and duni:
                deg_id = generate_prefixed_id('D')
                db.execute(
                    'INSERT INTO previous_deg (deg_id, app_id, dtype, dyear, dGPA, duni, dmajor) VALUES(?,?,?,?,?,?,?)',
                    [deg_id, aid, dtype, dyear or None, dgpa or None, duni, dmajor]
                )
        db.commit()

        # Recommendation
        rfname       = request.form.get('rfname', '')
        rlname       = request.form.get('rlname', '')
        remail       = request.form.get('remail', '')
        raffiliation = request.form.get('raffiliation', '')
        rtitle       = request.form.get('rtitle', '')
        submitted    = request.form.get('submitted', 'false')

        if recommendation:
            db.execute('''UPDATE recommendation SET rfname=?, rlname=?, remail=?, raffiliation=?, rtitle=?, submitted=?
                       WHERE app_id=?''', [rfname, rlname, remail, raffiliation, rtitle, submitted == 'true', aid])
        db.commit()

        # Transcript
        sent_date = request.form.get('sent_date', '') or None
        if transcript:
            db.execute('UPDATE transcripts SET received=?, received_date=? WHERE app_id=?', [1 if sent_date else 0,sent_date, aid])
        db.commit()

        # GRE
        verbal       = request.form.get('verbal', '') or None
        quantitative = request.form.get('quantitative', '') or None
        gre_total    = request.form.get('gre_total', '') or None
        exam_year    = request.form.get('exam_year', '') or None
        subj_score   = request.form.get('subj_score', '') or None
        subj_name    = request.form.get('subj_name', '') or None

        if gre:
            db.execute('''UPDATE gre SET verbal=?, quantitative=?, total=?, subj_score=?, subj_name=?, exam_year=?
                       WHERE app_id=?''', [verbal, quantitative, gre_total, subj_score, subj_name, exam_year, aid])
        
        update_application_completeness(aid)
        db.commit()

        flash('Application updated successfully', 'success')
        return redirect(url_for('apps.modify_user', username=username))

    return render_template('admin_edit_application.html', username=username,
                           appdata=appdata, degrees=degrees, gre=gre,
                           workex=workex, recommendation=recommendation, transcript=transcript, program=program, applicant=applicant)
    

@apps_bp.route('/dashboard/cac_gs/final_decision/<app_id>', methods=['GET', 'POST'])
@login_required
@role_required(3, 4)
def final_decision(app_id):
    db = get_db()
    username = session['user']['username']
    user = db.execute('SELECT * FROM users WHERE user_id=?', [username]).fetchone()

    application = db.execute("""SELECT * FROM applications 
        JOIN applicants ON applications.uid = applicants.uid
        JOIN soughtdeg ON applications.deg_no = soughtdeg.deg_no
        WHERE applications.app_id=?""",[app_id]).fetchone()

    if not application:
        flash('Application not found')
        return redirect(url_for('apps.cac_gs_dashboard'))

    if application['status'] != 'Reviewed':
        flash('Final decision can only be entered after all reviews are completed')
        return redirect(url_for('apps.cac_gs_dashboard'))

    reviews = db.execute("""SELECT * FROM review
        JOIN faculty ON review.reviewer_id = faculty.user_id
        WHERE app_id=? AND rating IS NOT NULL ORDER BY reviewer_id""", [app_id]).fetchall()

    avg_row = db.execute("""SELECT AVG(rating) AS average_rating FROM review
        WHERE app_id=? AND rating IS NOT NULL""", [app_id]).fetchone()

    average_rating = avg_row['average_rating'] if avg_row and avg_row['average_rating'] is not None else 'N/A'

    if request.method == 'POST':
        final_decision = request.form.get('final_decision')

        if not final_decision:
            flash('Please select a final decision')
            return render_template('final_decision.html',application=application,reviews=reviews,average_rating=average_rating)

        db.execute("UPDATE applications SET final_dec=?, status='Decision Made' WHERE app_id=?",
            [final_decision, app_id])

        # If admitted, promote the applicant to student role and create student record
        if final_decision in ('Admit', 'Admit with Aid'):
            applicant_rec = db.execute('SELECT * FROM applicants WHERE uid=?',[application['uid']]).fetchone()

            if applicant_rec:
                existing_student = db.execute('SELECT * FROM students WHERE uid=?',[application['uid']]).fetchone()

                if not existing_student:
                    student_user_id = f"student_{application['uid']}"
                    temp_password = generate_password_hash("changeme123")

                    existing_student_user = db.execute('SELECT * FROM users WHERE user_id=?',[student_user_id]).fetchone()

                    if not existing_student_user:
                        applicant_user = db.execute('SELECT * FROM users WHERE user_id=?',[applicant_rec['user_id']]).fetchone()

                        db.execute('INSERT INTO users (user_id, email, password, role_id) VALUES (?, ?, ?, ?)',
                        [
                            student_user_id,
                            f"{student_user_id}@gwu.edu",
                            temp_password,
                            1
                        ])

                    db.execute('''INSERT INTO students (uid, user_id, admit_app_id, start_semester, start_year) VALUES (?, ?, ?, ?, ?)''',
                        [
                            application['uid'],
                            student_user_id,
                            app_id,
                            application['semester'],
                            application['app_year']
                        ])

        db.commit()
        flash('Final decision recorded successfully')
        return redirect(url_for('apps.cac_gs_dashboard'))

    return render_template('final_decision.html', application=application, reviews=reviews, average_rating=average_rating)

@apps_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE user_id=?', [username]).fetchone()
        if not user:
            flash('No account found with that username.')
            return render_template('forgot_password.html')
        existing = db.execute(
            "SELECT * FROM password_reset_requests WHERE user_id=? AND status='Pending'",
            [username]).fetchone()
        if existing:
            flash('A reset request is already pending for this account.')
            return render_template('forgot_password.html')
        req_id = generate_prefixed_id('REQ')
        db.execute('INSERT INTO password_reset_requests (req_id, user_id) VALUES (?,?)',
                   [req_id, username])
        db.commit()
        flash('Reset request submitted. An admin will reset your password shortly.')
        return redirect(url_for('apps.login'))
    return render_template('forgot_password.html')

@apps_bp.route('/admin/password_reset')
@login_required
@role_required(5)
def admin_password_reset():
    db = get_db()
    requests = db.execute(
        "SELECT r.*, u.email FROM password_reset_requests r JOIN users u ON r.user_id=u.user_id WHERE r.status='Pending' ORDER BY r.requested_date"
    ).fetchall()
    return render_template('admin_password_reset.html', requests=requests)

@apps_bp.route('/admin/password_reset/<req_id>/reset', methods=['POST'])
@login_required
@role_required(5)
def admin_do_reset(req_id):
    db = get_db()
    req = db.execute('SELECT * FROM password_reset_requests WHERE req_id=?', [req_id]).fetchone()
    if not req:
        flash('Request not found.')
        return redirect(url_for('apps.admin_password_reset'))
    new_password = request.form.get('new_password', '').strip()
    if not new_password:
        flash('New password cannot be empty.')
        return redirect(url_for('apps.admin_password_reset'))
    db.execute('UPDATE users SET password=? WHERE user_id=?',
               [generate_password_hash(new_password), req['user_id']])
    db.execute("UPDATE password_reset_requests SET status='Resolved' WHERE req_id=?", [req_id])
    db.commit()
    flash(f"Password reset for {req['user_id']}.")
    return redirect(url_for('apps.admin_password_reset'))

@apps_bp.route('/admin/password_reset/<req_id>/dismiss', methods=['POST'])
@login_required
@role_required(5)
def admin_dismiss_reset(req_id):
    db = get_db()
    db.execute("UPDATE password_reset_requests SET status='Dismissed' WHERE req_id=?", [req_id])
    db.commit()
    flash('Request dismissed.')
    return redirect(url_for('apps.admin_password_reset'))


def init_apps(app):
    app.secret_key = app.secret_key or os.environ.get('SECRET_KEY', os.urandom(24))
    app.config.setdefault('SESSION_PERMANENT', False)
    app.config.setdefault('SESSION_TYPE', 'filesystem')
    Session(app)
