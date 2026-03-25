from flask import render_template
from utils.decorators import role_required
from . import student

@student.route('/')
@role_required('system_admin', 'student')
def index():
    return render_template('courses.html')

@student.route('/transcript')
@role_required('system_admin', 'student')
def transcript():
    return render_template('transcript.html')