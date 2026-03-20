from flask import Flask

from blueprints.auth import auth
from blueprints.staff import staff
from blueprints.student import student
from app.blueprints.main.main import main


def instance():
    app = Flask(__name__)
    app.secret_key = 'birdsarentreal'  # no enviromental variables for now, i don't wanna mess up with others machines [for now :)]

    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(staff, url_prefix='/staff')
    app.register_blueprint(student, url_prefix='/student')
    app.register_blueprint(main)
    
    return app