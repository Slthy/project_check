from flask import render_template
from utils.decorators import role_required
from . import faculty_instructor

@faculty_instructor.route('/')
@role_required('system_admin', 'faculty_instructor')
def index():
    return render_template('faculty_instructor.html')