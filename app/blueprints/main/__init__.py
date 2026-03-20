from flask import Blueprint

main = Blueprint(
    'main',
    __name__,
    template_folder='templates',  # Relative to Blueprint package
    static_folder='static',
    static_url_path='/main/static'  # URL path for static files
)