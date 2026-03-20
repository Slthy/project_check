from flask import render_template, request, session, flash, redirect
import sqlite3
from bcrypt import hashpw, checkpw, gensalt

from utils.functions import get_db_connection

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

        # 0, system_admin: creates everybody but cannot be created          
        # 1, grad_secretary: cannot register
        # 2, faculty_instructor: cannot register
        # 3, user: the only role that can be created without being system admin !!

        role = request.form['role'] if session.get('role') == 0 else 3  # role is "student" by default, unless a system admin is registring a new user   
        
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                (fname, lname, mname, email, password_hash, role)
            )
            conn.commit()
            return redirect('/login') if session.get('role') == 0 else redirect('/')
            
        except sqlite3.IntegrityError:
            flash("Email already exists.", "error")
        except sqlite3.Error as e:
            # Catch any other database errors so the app doesn't crash
            print(f"Database error during registration: {e}")
            flash("An error occurred during registration. Please try again.", "error")
            
        finally:
            if conn:
                conn.close()

    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = None
        user = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            user = cursor.execute(
                'SELECT * FROM users WHERE email = ?', (email,)     # single-value tuple trick
            ).fetchone()
            
        except sqlite3.Error as e:
            print(f"database error during login: {e}")
            flash("database error, try again.", "error")
            
        finally:
            if conn:
                conn.close()

        if user and checkpw(password.encode('utf-8'), user['password']):
            session.clear()
            session['email'] = user['email']
            session['uid'] = user['uid']
            session['role'] = user['role']                      # store role

            flash(f"Welcome back, {user['fname']}!", "success")
            return redirect('/')
        else:
            flash("Invalid email or password.", "error")

    return render_template('login.html')

@auth.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/login')
