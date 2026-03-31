"""
System administrator routes: user management, database reset, and documentation serving.

All routes (except serve_sphinx_docs) require an authenticated session with
role 'system_admin'. Routes are registered on the 'system_admin' blueprint
under /system_admin.
"""

from flask import render_template, request, redirect, url_for, flash, session, send_from_directory, current_app 
from utils.decorators import role_required, login_required
from utils.functions import get_db_connection, to_minutes
from utils.log_collector import admin_log_handler
from . import system_admin
import sqlite3, shutil, os


@system_admin.app_context_processor
def inject_admin_logs():
    if session.get('role') == 0:
        return dict(logs=admin_log_handler.get_records())
    return dict(logs=[])

@system_admin.route('/')
@login_required
@role_required('system_admin')
def index():
    """
    Redirect the system admin to the application home page.
    """
    return redirect(url_for('home'))

@system_admin.route('/users')
@login_required
@role_required('system_admin')
def view_users():
    """
    Render a paginated list of all users in the system.

    Fetches id, first name, last name, email, and role for every user,
    ordered by ID.
    """
    admin_id = session.get('user_id', 'Unknown')
    users = []
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        users = cursor.execute(
            'SELECT id, fname, lname, email, role FROM users ORDER BY id'
        ).fetchall()
        
        current_app.logger.info(f"Admin {admin_id} accessed the global user list.")
        
    except sqlite3.Error as e:
        flash("Error loading users.", "error")
        current_app.logger.error(f"DB error in view_users: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('view_users.html', users=users)

@system_admin.route('/users/delete', methods=['POST'])
@login_required
@role_required('system_admin')
def delete_user():
    """
    Delete a user account by ID (POST only).
    """
    admin_id = session.get('user_id', 'Unknown')
    user_id = request.form['user_id']
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        flash("User deleted successfully.", "success")
        
        current_app.logger.info(f"Admin {admin_id} securely deleted user ID {user_id}.")
        
    except sqlite3.Error as e:
        flash("Error deleting user.", "error")
        current_app.logger.error(f"DB error in delete_user: {e}")
    finally:
        if conn:
            conn.close()

    return redirect(url_for('system_admin.view_users'))

@system_admin.route('/reset')
# @login_required                   REVERT POST DEMO
# @role_required('system_admin')    REVERT POST DEMO
def shutdown():
    """
    Reset the database to a clean seed state and redirect to login.
    """
    admin_id = session.get('user_id', 'Unknown')
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    live_db = os.path.join(base, 'database.db')
    backup_db = os.path.join(base, 'reset', 'database.db')

    if os.path.exists(live_db):
        os.remove(live_db)
    shutil.copy(backup_db, base)

    current_app.logger.critical(f"Admin {admin_id} INITIATED A FULL DATABASE RESET. The system was wiped and seeded.") 

    return redirect(url_for('auth.login'))


@system_admin.route('/docs/')
@system_admin.route('/docs/<path:filename>')
@login_required
@role_required('system_admin')
def serve_sphinx_docs(filename='index.html'):
    """
    Serve static files from the Sphinx HTML documentation build.
    """
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../docs/build/html'))
    return send_from_directory(docs_dir, filename)


@system_admin.route('/users/edit/<int:uid>', methods=['GET', 'POST'])
@login_required
@role_required('system_admin')
def edit_user(uid):
    admin_id = session.get('user_id', 'Unknown')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if request.method == 'GET':
            current_app.logger.info(f"Admin {admin_id} accessed the edit page for user ID {uid}.")

        if request.method == 'POST':
            email = request.form.get('email')
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            line_one = request.form.get('line_one')
            line_two = request.form.get('line_two')
            city = request.form.get('city')
            state = request.form.get('state')
            zip_code = request.form.get('zip')
            country_code = request.form.get('country_code')

            try:
                cursor.execute('''
                    UPDATE users SET fname = ?, lname = ?, email = ?
                    WHERE id = ?
                ''', (fname, lname, email, uid))
                cursor.execute('''
                    UPDATE addresses SET line_one = ?, line_two = ?,
                        city = ?, state = ?, zip = ?, country_code = ?
                    WHERE a_id = ?
                ''', (line_one, line_two, city, state, zip_code, country_code, uid))
                conn.commit()
                flash("User updated successfully.", "success")

                current_app.logger.info(f"Admin {admin_id} successfully updated account details for user ID {uid}.") 
                return redirect(url_for('system_admin.view_users'))
                
            except sqlite3.IntegrityError:
                flash("That email is already in use.", "error")
                current_app.logger.warning(f"Admin {admin_id} failed to update user {uid}: Email '{email}' is already in use.") 

        user = cursor.execute('SELECT * FROM users WHERE id = ?', (uid,)).fetchone()
        address = cursor.execute('SELECT * FROM addresses WHERE a_id = ?', (uid,)).fetchone()

        assigned_courses = []
        available_courses = []

        if user and user['role'] == 2:
            assigned_courses = cursor.execute('''
                SELECT o.o_id, c.dept, c.number, c.name,
                       s.day, s.start_time, s.end_time
                FROM c_offering o
                JOIN c_catalog c ON o.c_id = c.c_id
                LEFT JOIN schedule s ON o.o_id = s.o_id
                WHERE o.i_id = ?
            ''', (uid,)).fetchall()

            assigned_o_ids = {c['o_id'] for c in assigned_courses}
            assigned_times = [
                (c['day'], c['start_time'], c['end_time'])
                for c in assigned_courses
                if c['day'] and c['start_time'] and c['end_time']
            ]
            all_courses = cursor.execute('''
                SELECT o.o_id, c.dept, c.number, c.name,
                       s.day, s.start_time, s.end_time
                FROM c_offering o
                JOIN c_catalog c ON o.c_id = c.c_id
                LEFT JOIN schedule s ON o.o_id = s.o_id
                WHERE o.i_id IS NULL OR o.i_id != ?
            ''', (uid,)).fetchall()

            for course in all_courses:
                if course['o_id'] in assigned_o_ids:
                    continue
                if not course['day'] or not course['start_time'] or not course['end_time']:
                    continue
                conflict = False
                for day, start, end in assigned_times:
                    if course['day'] != day:
                        continue
                    cs = to_minutes(course['start_time'])
                    ce = to_minutes(course['end_time'])
                    es = to_minutes(start)
                    ee = to_minutes(end)
                    if not (cs >= ee + 30 or ce <= es - 30):
                        conflict = True
                        break
                if not conflict:
                    available_courses.append(course)

    except sqlite3.Error as e:
        flash("Error loading user.", "error")
        current_app.logger.warning(f"DB error in edit_user: {e}") 
        user = None
        address = None
        assigned_courses = []
        available_courses = []
    finally:
        if conn:
            conn.close()

    return render_template('edit_user.html', user=user, address=address,
                           assigned_courses=assigned_courses,
                           available_courses=available_courses)


@system_admin.route('/users/edit/<int:uid>/assign', methods=['POST'])
@login_required
@role_required('system_admin')
def assign_course(uid):
    admin_id = session.get('user_id', 'Unknown')
    o_id = request.form.get('o_id')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE c_offering SET i_id = ? WHERE o_id = ?', (uid, o_id))
        conn.commit()
        flash("Course assigned successfully.", "success")
        
        current_app.logger.info(f"Admin {admin_id} assigned course offering {o_id} to faculty ID {uid}.") 
        
    except sqlite3.Error as e:
        flash("Error assigning course.", "error")
        current_app.logger.warning(f"DB error in assign_course: {e}") 
    finally:
        if conn:
            conn.close()
    return redirect(url_for('system_admin.edit_user', uid=uid))


@system_admin.route('/users/edit/<int:uid>/unassign/<int:o_id>', methods=['POST'])
@login_required
@role_required('system_admin')
def unassign_course(uid, o_id):
    admin_id = session.get('user_id', 'Unknown')
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE c_offering SET i_id = NULL WHERE o_id = ? AND i_id = ?', (o_id, uid))
        conn.commit()
        flash("Course unassigned successfully.", "success")

        current_app.logger.info(f"Admin {admin_id} unassigned course offering {o_id} from faculty ID {uid}.") 
        
    except sqlite3.Error as e:
        flash("Error unassigning course.", "error")
        current_app.logger.warning(f"DB error in unassign_course: {e}") 
    finally:
        if conn:
            conn.close()
    return redirect(url_for('system_admin.edit_user', uid=uid))


@system_admin.route('/logs/clear', methods=['POST'])
@login_required
@role_required('system_admin')
def clear_logs():
    admin_id = session.get('user_id', 'Unknown')
    admin_log_handler.clear()
    flash("Application logs cleared.", "success")

    current_app.logger.warning(f"Admin {admin_id} wiped the in-memory application logs.")
    
    return redirect(request.referrer or url_for('home'))