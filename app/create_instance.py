"""
Flask application factory.

Call instance() to create and configure the Flask app with all blueprints
registered and the two app-level routes (home dashboard and about me) attached.
"""

from flask import Flask, session, render_template, redirect, request, flash, url_for
import sqlite3

from blueprints.auth import auth
from blueprints.faculty_instructor import faculty_instructor
from blueprints.grad_secretary import grad_secretary
from blueprints.student import student
from blueprints.system_admin import system_admin

from utils.functions import get_db_connection
from utils.decorators import login_required

from flask_babel import Babel, _

from utils.logger import setup_logger

from utils.log_collector import admin_log_handler

babel = Babel()

def instance():
    """
    Create, configure, and return the Flask application.

    Registers all blueprints under their respective URL prefixes, sets the
    secret key, and defines the '/' and '/about_me' routes directly on the
    app (since they are role-agnostic and do not belong to any blueprint).

    Returns:
        Flask: The fully configured application instance.
    """
    app = Flask(__name__)
    app.secret_key = 'birdsarentreal'
    app.config['LANGUAGES'] = ['en', 'it', 'ar', 'es', 'fr', 'hi']
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'

    def get_locale():
        if 'lang' in session:
            return session['lang']

        return request.accept_languages.best_match(['en', 'it', "ar", "es"])

    babel.init_app(app, locale_selector=get_locale)

    setup_logger(app)

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(faculty_instructor, url_prefix='/faculty_instructor')
    app.register_blueprint(grad_secretary, url_prefix='/grad_secretary')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(system_admin, url_prefix='/system_admin')

    @app.route('/set_language', methods=['POST'])
    def set_language():

        language = request.form.get('language')
        
        if language in ['en', 'it', 'ar', 'es', 'fr', 'hi']:
            session['lang'] = language

        return redirect(request.referrer or url_for('home'))

    @app.route('/')
    def home():
        if 'role' not in session:
            return redirect('/auth/login')

        conn = get_db_connection()
        cursor = conn.cursor()
        user = cursor.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
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
                        'UPDATE users SET email = ? WHERE id = ?',
                        (email, session['user_id'])
                    )
                    cursor.execute('''
                        UPDATE addresses SET line_one = ?, line_two = ?,
                            city = ?, state = ?, zip = ?, country_code = ?
                        WHERE a_id = ?
                    ''', (line_one, line_two, city, state, zip_code,
                        country_code, session['user_id']))
                    conn.commit()
                    flash(_("Profile updated successfully."), "success")
                    app.logger.info(f"User {session['user_id']}'s account has been updated successfully.")
                    session['email'] = email
                except sqlite3.IntegrityError:
                    flash(_("That email is already in use."), "error")
                    app.logger.warning(f"User {session['user_id']}'s account update has failed. constraint: email")

            user = cursor.execute(
                'SELECT * FROM users WHERE id = ?', (session['user_id'],)
            ).fetchone()
            address = cursor.execute(
                'SELECT * FROM addresses WHERE a_id = ?', (session['user_id'],)
            ).fetchone()

        except sqlite3.Error as e:
            flash(_("Error loading profile."), "error")
            app.logger.error(f"DB error in view_users: {e}")
            user = None
            address = None
        finally:
            if conn:
                conn.close()

        return render_template('about_me.html', data=user, address=address)

    return app