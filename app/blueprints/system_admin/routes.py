from flask import render_template
from utils.decorators import role_required
from . import system_admin

@system_admin.route('/')
@role_required('system_admin')
def index():
    return render_template('auth/sys_admin_register.html')