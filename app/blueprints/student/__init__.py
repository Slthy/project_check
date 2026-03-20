from flask import Blueprint

student = Blueprint(
    'student',
    __name__,
    template_folder='templates',  # Relative to Blueprint package
    static_folder='static',
    static_url_path='/student/static'  # URL path for static files
)