import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Blueprint, g

ADS_DIR = Path(__file__).resolve().parent
if str(ADS_DIR) not in sys.path:
    sys.path.insert(0, str(ADS_DIR))

from routes.auth import auth_bp
from routes.student import student_bp
from routes.advisor import advisor_bp
from routes.gs import gs_bp
from routes.alumni import alumni_bp
from routes.admin import admin_bp

load_dotenv()

ads_bp = Blueprint('ads', __name__, template_folder='templates', static_folder='static')
ads_bp.register_blueprint(auth_bp)
ads_bp.register_blueprint(student_bp)
ads_bp.register_blueprint(advisor_bp)
ads_bp.register_blueprint(gs_bp)
ads_bp.register_blueprint(alumni_bp)
ads_bp.register_blueprint(admin_bp)


@ads_bp.teardown_app_request
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_ads(app):
    app.secret_key = app.secret_key or os.environ.get('FLASK_SECRET_KEY')
    app.jinja_env.globals['flask_debug'] = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
