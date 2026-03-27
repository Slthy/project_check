import sqlite3
import os

def get_db_connection():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', '..', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def has_time_conflict(current_schedule, new_times):
    def to_minutes(t):
        h, m = map(int, t.split(':'))
        return h * 60 + m

    for new in new_times:
        new_start = to_minutes(new['start_time'])
        new_end = to_minutes(new['end_time'])
        for existing in current_schedule:
            if existing['day'] != new['day']:
                continue
            ex_start = to_minutes(existing['start_time'])
            ex_end = to_minutes(existing['end_time'])
            # must have at least 30 min gap
            if not (new_start >= ex_end + 30 or new_end <= ex_start - 30):
                return True
    return False