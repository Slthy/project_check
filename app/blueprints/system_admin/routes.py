from flask import render_template, request, redirect, url_for, flash, session, send_from_directory
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection
from . import system_admin
import sqlite3, shutil, os

@system_admin.route('/')
@login_required
@role_required('system_admin')
def index():
    return redirect(url_for('home'))

@system_admin.route('/users')
@login_required
@role_required('system_admin')
def view_users():
    users = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        users = cursor.execute(
            'SELECT id, fname, lname, email, role FROM users ORDER BY id'
        ).fetchall()
    except sqlite3.Error as e:
        flash("Error loading users.", "error")
        print(f"DB error in view_users: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('view_users.html', users=users)

@system_admin.route('/users/delete', methods=['POST'])
@login_required
@role_required('system_admin')
def delete_user():
    user_id = request.form['user_id']

    if int(user_id) == session['user_id']:
        flash("You cannot delete your own account while logged in.", "error")
        return redirect(url_for('system_admin.view_users'))

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash("User deleted successfully.", "success")
    except sqlite3.Error as e:
        flash("Error deleting user.", "error")
        print(f"DB error in delete_user: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('system_admin.view_users'))

@system_admin.route('/reset')
def shutdown():
    if os.path.exists("../26-project-phase1-birdsarentreal/database.db"):
        os.remove("../26-project-phase1-birdsarentreal/database.db")
    shutil.copy("../26-project-phase1-birdsarentreal/reset/database.db", "../26-project-phase1-birdsarentreal")

    return redirect(url_for('auth.login'))

@system_admin.route('/docs/')
@system_admin.route('/docs/<path:filename>')
def serve_sphinx_docs(filename='index.html'):
    # Calculate the absolute path to your Sphinx HTML build directory
    # Adjust os.path.dirname(__file__) based on where this script actually lives
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../docs/build/html'))
    
    # Securely send the requested file from the docs directory
    return send_from_directory(docs_dir, filename)