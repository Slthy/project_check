from functools import wraps
from flask import session, redirect, url_for
from db import get_db


# Numeric role IDs matching the roles table.
class Role:
    ADMIN = 1
    GS = 2
    ADVISOR = 3
    STUDENT = 4
    ALUMNI = 5


# Re-validate the current user's role from the DB and reject if unauthorized.
# session['role_id'] is updated from the DB result and used only for UI convenience — not as an auth gate.
def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('auth.login'))
            user = get_db().execute(
                'SELECT role_id FROM users WHERE user_id = %s',
                (session['user_id'],)
            ).fetchone()
            if not user or user['role_id'] not in roles:
                session.clear()
                return redirect(url_for('auth.login'))
            session['role_id'] = user['role_id']
            return f(*args, **kwargs)
        return decorated_function
    return decorator
