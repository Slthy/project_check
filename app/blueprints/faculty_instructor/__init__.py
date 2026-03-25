from flask import Blueprint

faculty_instructor = Blueprint(
    'faculty_instructor',
    __name__,
    template_folder='templates',  # Relative to Blueprint package
    static_folder='static',
    static_url_path='/auth/static'  # URL path for static files
)

from . import routes