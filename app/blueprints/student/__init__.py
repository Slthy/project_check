from flask import Blueprint

student = Blueprint(
    'student',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/student'
)

from . import routes