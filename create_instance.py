"""
Flask application factory.

Call instance() to create and configure the Flask app with all blueprints
registered and the app-level routes (landing, REGS home, dashboard, and about me).
"""

from flask import Flask, session, render_template, redirect, request, flash, url_for
import pymysql

from REGS.blueprints.auth import auth
from REGS.blueprints.faculty_instructor import faculty_instructor
from REGS.blueprints.grad_secretary import grad_secretary
from REGS.blueprints.student import student
from REGS.blueprints.system_admin import system_admin

from ADS.main import ads_bp, init_ads
from APPS.main import apps_bp, init_apps

from utils.functions import get_db_connection
from utils.decorators import login_required

from flask_babel import Babel, _

from utils.logger import setup_logger
from utils.log_collector import admin_log_handler

babel = Babel()



def instance():
    """Create, configure, and return the Flask application."""
    app = Flask(__name__)
    app.secret_key = 'birdsarentreal'
    app.config['LANGUAGES'] = ['en', 'it', 'ar', 'es', 'fr', 'hi']
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    def get_locale():
        if 'lang' in session:
            return session['lang']
        return request.accept_languages.best_match(['en', 'it', 'ar', 'es', 'fr', 'hi'])

    babel.init_app(app, locale_selector=get_locale)
    setup_logger(app)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(faculty_instructor, url_prefix='/faculty_instructor')
    app.register_blueprint(grad_secretary, url_prefix='/grad_secretary')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(system_admin, url_prefix='/system_admin')
    app.register_blueprint(ads_bp, url_prefix='/ads')
    app.register_blueprint(apps_bp, url_prefix='/apps')

    init_ads(app)
    init_apps(app)

    @app.route('/set_language', methods=['POST'])
    def set_language():
        language = request.form.get('language')
        if language in ['en', 'it', 'ar', 'es', 'fr', 'hi']:
            session['lang'] = language
        return redirect(request.referrer or url_for('home'))

    @app.route('/')
    def landing():
        return render_template('index.html')

    @app.route('/regs')
    def home():
        if 'role' not in session:
            return render_template('regs_home.html')

        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    def dashboard():
        if 'role' not in session:
            return redirect('/auth/login')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()

        logs = []
        if session.get('role') == 0:
            logs = admin_log_handler.get_records()

        return render_template('dashboard.html', data=user, logs=logs)

    @app.route('/about_me', methods=['GET', 'POST'])
    @login_required
    def about_me():
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            if request.method == 'POST':
                email = request.form.get('email')
                line_one = request.form.get('line_one')
                line_two = request.form.get('line_two')
                city = request.form.get('city')
                state = request.form.get('state')
                zip_code = request.form.get('zip')
                country_code = request.form.get('country_code')

                try:
                    cursor.execute(
                        'UPDATE users SET email = %s WHERE id = %s',
                        (email, session['user_id'])
                    )
                    cursor.execute(
                        '''
                        UPDATE addresses SET line_one = %s, line_two = %s,
                            city = %s, state = %s, zip = %s, country_code = %s
                        WHERE a_id = %s
                        ''',
                        (line_one, line_two, city, state, zip_code, country_code, session['user_id'],),
                    )
                    conn.commit()
                    flash(_('Profile updated successfully.'), 'success')
                    app.logger.info(
                        f"User {session['user_id']}'s account has been updated successfully."
                    )
                    session['email'] = email
                except pymysql.IntegrityError:
                    flash(_('That email is already in use.'), 'error')
                    app.logger.warning(
                        f"User {session['user_id']}'s account update has failed. constraint: email"
                    )

            cursor.execute('SELECT * FROM users WHERE id = %s', (session['user_id'],))
            user = cursor.fetchone()
            cursor.execute('SELECT * FROM addresses WHERE a_id = %s', (session['user_id'],))
            address = cursor.fetchone()

        except pymysql.Error as e:
            flash(_('Error loading profile.'), 'error')
            app.logger.error(f'DB error in view_users: {e}')
            user = None
            address = None
        finally:
            if conn:
                conn.close()

        return render_template('about_me.html', data=user, address=address)

    return app
