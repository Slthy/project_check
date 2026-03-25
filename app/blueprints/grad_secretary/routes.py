from flask import render_template
from utils.decorators import role_required
from . import grad_secretary

@grad_secretary.route('/')
@role_required('system_admin', 'grad_secretary')
def index():
    return render_template('grad_secretary.html')