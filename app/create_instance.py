from flask import Flask, session, render_template, redirect

from blueprints.auth import auth
from blueprints.faculty_instructor import faculty_instructor
from blueprints.grad_secretary import grad_secretary
from blueprints.student import student
from blueprints.system_admin import system_admin

from utils.functions import get_db_connection
from utils.decorators import login_required

def instance():
    app = Flask(__name__)
    app.secret_key = 'birdsarentreal'  # no enviromental variables for now, i don't wanna mess up with others machines [for now :)]

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(faculty_instructor, url_prefix='/faculty_instructor')
    app.register_blueprint(grad_secretary, url_prefix='/grad_secretary')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(system_admin, url_prefix='/system_admin')

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

        return render_template('dashboard.html', data=user)
    
    @app.route('/about_me')
    @login_required
    def about_me():
        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute(
            'SELECT * FROM users WHERE id = ?', (session['user_id'],)
        ).fetchone()
        conn.close()

        return render_template('about_me.html', data=user)

    return app