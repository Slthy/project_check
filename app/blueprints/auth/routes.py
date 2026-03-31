"""
Authentication routes: registration, login, logout, and admin user creation.

All routes in this module are registered on the 'auth' blueprint and are
accessible under the /auth URL prefix.
"""

from flask import render_template, request, session, flash, redirect, url_for, current_app
import sqlite3
from bcrypt import hashpw, checkpw, gensalt

from utils.functions import get_db_connection
from utils.decorators import role_required

from flask_babel import _

from . import auth

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
        admin_id = session.get('user_id', 'Unknown')

        if request.form['role'] in ['0', '1', '2', '3']:
            role = int(request.form['role'])
            conn = get_db_connection()
            cursor = conn.cursor()

            existing_user = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing_user:
                flash(_("Email already exists."), "error")
                current_app.logger.warning(f"Admin {admin_id} failed to create user: Email '{email}' is already in use.")
                conn.close()
                return render_template('auth/sys_admin_register.html')

            try:
                max_id_row = cursor.execute("SELECT MAX(id) FROM users WHERE id < 90000000").fetchone()
                new_id = (max_id_row[0] + 1) if max_id_row[0] else 10000000
                cursor.execute(
                    "INSERT INTO users (id, fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (new_id, fname, lname, mname, email, password_hash, role)
                )
                last_id = cursor.lastrowid

                if role == 3:
                    cursor.execute(
                        "INSERT INTO stud_type (id, track, admit_year) VALUES (?, ?, ?)",
                        (last_id, request.form['track'], request.form['admit_year'])
                    )

                cursor.execute(
                    "INSERT INTO addresses (a_id, line_one, line_two, city, state, zip, country_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (last_id, request.form['line_one'], request.form.get('line_two'),
                    request.form['city'], request.form['state'], request.form['zip'], request.form['country_code'])
                )
                conn.commit()
                flash(_("User created successfully."), "success")
                
                current_app.logger.info(f"Admin {admin_id} successfully created user {last_id} (Role: {role}, Email: {email})")
                
                return redirect(url_for('system_admin.view_users'))
            
            except sqlite3.IntegrityError as e:
                flash(_("A database error occurred. Ensure all required fields are filled."), "error")
                current_app.logger.error(f"IntegrityError during admin user creation: {e}")
                
            finally:
                conn.close()
        else:
            flash(_("Invalid role selected."), "error")
            current_app.logger.warning(f"Admin {admin_id} attempted to create a user with invalid role '{request.form.get('role')}'.")

    return render_template('auth/sys_admin_register.html') 


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        mname = request.form['mname'] if request.form['mname'] else None
        email = request.form['email']
        password = request.form['password']
        password_hash = hashpw(password.encode('utf-8'), gensalt())
        role = 3

        conn = get_db_connection()
        cursor = conn.cursor()

        existing_user = cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing_user:
            flash(_("Email already exists."), "error")
            current_app.logger.warning(f"Self-registration failed: Email '{email}' is already in use.")
            conn.close()
            return render_template('auth/register.html')

        try:
            max_id_row = cursor.execute("SELECT MAX(id) FROM users WHERE id < 90000000").fetchone()
            new_id = (max_id_row[0] + 1) if max_id_row[0] else 10000000
            cursor.execute(
                "INSERT INTO users (id, fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (new_id, fname, lname, mname, email, password_hash, role)
            )
            last_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO stud_type (id, track, admit_year) VALUES (?, ?, ?)",
                (last_id, request.form['track'], request.form['admit_year'])
            )
            cursor.execute(
                "INSERT INTO addresses (a_id, line_one, line_two, city, state, zip, country_code) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (last_id, request.form['line_one'], request.form.get('line_two'),
                request.form['city'], request.form['state'], request.form['zip'], request.form['country_code'])
            )
            conn.commit()

            current_app.logger.info(f"New student successfully self-registered with ID {last_id} (Email: {email})")
            
            return redirect('/auth/login')
            
        except sqlite3.IntegrityError as e:
            flash(_("A database error occurred. Ensure all required fields are filled."), "error")
            current_app.logger.error(f"IntegrityError during self-registration: {e}")
            
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

        stored_password: bytes = b''
        if user:
            stored_password = user['password']
            if isinstance(stored_password, str):
                stored_password = stored_password.encode('utf-8')

        if user and checkpw(password.encode('utf-8'), stored_password):
            session.clear()
            session['email'] = user['email']
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash(_("Welcome back, %(name)s!", name=user['fname']), "success")
            return redirect('/')
        else:
            flash(_("Invalid email or password."), "error")

    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.clear()
    return redirect('/auth/login')