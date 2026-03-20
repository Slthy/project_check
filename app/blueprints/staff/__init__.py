from flask import Blueprint

staff = Blueprint(
    'staff',
    __name__,
    template_folder='templates',  # Relative to Blueprint package
    static_folder='static',
    static_url_path='/staff/static'  # URL path for static files
)