from flask import render_template, request, session, flash, redirect
import sqlite3
from bcrypt import hashpw, checkpw, gensalt

from utils.functions import get_db_connection
from utils.decorators import role_required

from . import auth

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname'] if request.form['mname'] else None
        email = request.form['email']
        password = request.form['password']
        password_hash = hashpw(password.encode('utf-8'), gensalt())

        role = 3    # 0, system_admin: creates everybody but cannot be created
                    # 1, grad_secretary: cannot register
                    # 2, faculty_instructor: cannot register
                    # 3, user: the only role that can be created without being system admin !!

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                (fname, lname, mname, email, password_hash, role)
            )
            conn.commit()
            return redirect('/auth/login')
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
        finally:
            conn.close()

    return render_template('auth/register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        user = cursor.execute(
            'SELECT * FROM users WHERE email = ?', (email,)
        ).fetchone()
        conn.close()

        stored_password = None
        if user:
            stored_password = user['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

        if user and checkpw(password.encode('utf-8'), stored_password):
            session.clear()
            session['email'] = user['email']
            session['user_id'] = user['id']
            session['role'] = user['role']

            flash(f"Welcome back, {user['fname']}!", "success")

            if user['role'] == 0:
                return redirect('/auth/sys_admin/register')
            elif user['role'] == 1:
                return redirect('/grad_secretary/')
            elif user['role'] == 2:
                return redirect('/faculty_instructor/')
            elif user['role'] == 3:
                return redirect('/student/')
            else:
                flash("Unknown role.", "error")
                return redirect('/auth/login')
        else:
            flash("Invalid email or password.", "error")

    return render_template('auth/login.html')

@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/auth/login')

@auth.route('/sys_admin/register', methods=['GET', 'POST'])
@role_required('system_admin')
def sys_admin_register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname'] if request.form['mname'] else None
        email = request.form['email']
        password = request.form['password']
        password_hash = hashpw(password.encode('utf-8'), gensalt())

        if request.form['role'] in ['1', '2', '3']:
            role = int(request.form['role'])
            conn = get_db_connection()
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO users (fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                    (fname, lname, mname, email, password_hash, role)
                )
                conn.commit()
                return redirect('/auth/login')
            except sqlite3.IntegrityError:
                flash("Email already exists.", "error")
            finally:
                conn.close()
        else:
            flash("System admins can only create 'Graduate Secretary', 'Faculty Instructor' or 'Graduate Student' accounts", "error")
    return render_template('auth/sys_admin_register.html')  # Ahmad, you can probably play a little with 
                                                        # templates and create a base login template that extents the base app template
                                                        # and two different login variations: students and sys-admin
