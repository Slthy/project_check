from functools import wraps
from flask import session, flash, redirect, abort

ROLES = {
    'system_admin': 0,
    'grad_secretary': 1,
    'faculty_instructor': 2,
    'student': 3
}

STAFF = {
    'system_admin': 0,
    'grad_secretary': 1,
    'faculty_instructor': 2
}

def login_required(f):                                              # reject unauthenticated users
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'uid' not in session:
            flash("Please log in to continue.", "error")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated

def is_staff(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if 'uid' not in session: # enforece login                           
            flash("Please log in to continue.", "error")
            return redirect('/login')
        
        user_role = session.get('role')
        
        if user_role not in [0, 1, 2]:  # check roles                
            abort(403)

        return f(*args, **kwargs)
        
    return decorated

def role_required(*roles):
    allowed = {ROLES[r] for r in roles}                             # get allowed roles by calling the ROLES dict

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'uid' not in session:                            # enforce log-in
                flash("Please log in to continue.", "error")
                return redirect('/login')
            if session.get('role') not in allowed:                  # enforce role if required
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return decorator