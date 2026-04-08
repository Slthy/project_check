import logging, os
from logging.handlers import RotatingFileHandler

from utils.log_collector import admin_log_handler


def setup_logger(app):
    log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'regs.log'),
        maxBytes=1_000_000,
        backupCount=3
    )

    file_handler.setLevel(logging.DEBUG)        # write file
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler() 
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    app.logger.setLevel(logging.DEBUG)          # console warnings
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)

    admin_log_handler.setLevel(logging.DEBUG)   # pipe logs to frontend
    admin_log_handler.setFormatter(formatter)
    app.logger.addHandler(admin_log_handler)