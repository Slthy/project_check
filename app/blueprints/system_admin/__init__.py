from flask import Blueprint

system_admin = Blueprint(
    'system_admin',
    __name__,
    template_folder='templates',  # Relative to Blueprint package
    static_folder='static',
    url_prefix='/system_admin'
)

from . import routes