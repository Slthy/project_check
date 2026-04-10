import os
from dotenv import load_dotenv
from flask import Flask, g

from routes.auth import auth_bp
from routes.student import student_bp
from routes.advisor import advisor_bp
from routes.gs import gs_bp
from routes.alumni import alumni_bp
from routes.admin import admin_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ['FLASK_SECRET_KEY']

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(advisor_bp)
app.register_blueprint(gs_bp)
app.register_blueprint(alumni_bp)
app.register_blueprint(admin_bp)


@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


app.jinja_env.globals['flask_debug'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'false').lower() == 'true')
