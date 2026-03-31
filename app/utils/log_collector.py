import logging
from collections import deque
from datetime import datetime


class AdminLogHandler(logging.Handler):

    def __init__(self, max_entries=200):
        super().__init__()
        self.records = deque(maxlen=max_entries)

    def emit(self, record):
        self.records.append({
            'time':    datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S'),
            'level':   record.levelname,
            'module':  record.module,
            'message': record.getMessage(),
        })

    def get_records(self):
        return list(self.records)

    def clear(self):
        self.records.clear()


admin_log_handler = AdminLogHandler()