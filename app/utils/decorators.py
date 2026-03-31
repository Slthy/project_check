"""
Authentication and authorization decorators for Flask route protection.

ROLES maps human-readable role names to the integer values stored in the
database and session, matching the CHECK constraint in users.sql.
"""

from functools import wraps
from flask import session, flash, redirect, abort

ROLES = {
    'system_admin': 0,
    'grad_secretary': 1,
    'faculty_instructor': 2,
    'student': 3
}

def login_required(f):                                               # reject unauthenticated users
    """
    Decorator that rejects unauthenticated requests.

    Redirects to the login page with a flash message if 'user_id' is
    not present in the session.

    Args:
        f (callable): The route function to protect.

    Returns:
        callable: The wrapped function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to continue.", "error")
            return redirect('/auth/login')
        return f(*args, **kwargs)
    return decorated

def role_required(*roles):
    """
    Decorator factory that restricts a route to one or more named roles.

    Accepts any number of role name strings (e.g., 'system_admin',
    'grad_secretary'). Unauthenticated requests are redirected to login;
    authenticated requests from disallowed roles receive a 403.

    Args:
        *roles (str): One or more keys from the ROLES dict.

    Returns:
        callable: A decorator that wraps the target route function.
    """
    allowed = {ROLES[r] for r in roles}                             # get allowed roles by calling the ROLES dict

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:                            # enforce log-in
                flash("Please log in to continue.", "error")
                return redirect('/auth/login')
            if session.get('role') not in allowed:                  # enforce role if required
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator