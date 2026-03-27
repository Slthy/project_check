from flask import render_template, request, session, flash, redirect, url_for
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
        role = 3

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (fname, lname, mname, email, password, role) VALUES (?, ?, ?, ?, ?, ?)",
                (fname, lname, mname, email, password_hash, role)
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
            flash(f"Welcome back, {user['fname']}!", "success")
            return redirect('/')
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
                flash("User created successfully.", "success")
                return redirect(url_for('system_admin.view_users'))
            except sqlite3.IntegrityError:
                flash("Email already exists.", "error")
            finally:
                conn.close()
        else:
            flash("Invalid role selected.", "error")

    return render_template('auth/sys_admin_register.html')  # Ahmad, you can probably play a little with 
                                                            # templates and create a base login template that extents the base app template
                                                            # and two different login variations: students and sys-admin