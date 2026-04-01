"""
Shared utility functions used across all blueprints.
"""

import pymysql
import pymysql.cursors
from datetime import timedelta

DB_CONFIG = {
    'host':     'regs26-borsato.cng0skw0wk8a.us-east-1.rds.amazonaws.com',
    'port':     3306,
    'database': 'university',
    'user':     'birdsarenotreal',
    'password': 'birdsarenotreal123',
    'cursorclass': pymysql.cursors.DictCursor,
    'charset':  'utf8mb4',
}

def get_db_connection():
    """
    Open and return a connection to the MySQL database on AWS RDS.

    Uses DictCursor so columns are accessible by name, matching the
    sqlite3.Row behaviour used throughout the application.

    Returns:
        pymysql.connections.Connection: An open database connection.
    """
    return pymysql.connect(**DB_CONFIG)

def to_minutes(t):
    """
    Convert a time value to total minutes since midnight.

    Accepts either a ``datetime.timedelta`` (as returned by PyMySQL for TIME
    columns) or a ``'HH:MM'`` / ``'HH:MM:SS'`` string.

    Args:
        t (timedelta | str): The time value to convert.

    Returns:
        int: Total minutes since midnight.
    """
    if isinstance(t, timedelta):
        return int(t.total_seconds() // 60)
    parts = str(t).split(':')
    return int(parts[0]) * 60 + int(parts[1])

def has_time_conflict(current_schedule, new_times):
    """
    Determine whether a set of new course times conflicts with an existing schedule.

    Two time slots conflict if they share the same day and do not have at least
    a 30-minute gap between them.

    Args:
        current_schedule (list[dict]): Dicts containing 'day', 'start_time',
            and 'end_time' for each currently enrolled course.
        new_times (list[dict]): Dicts with the same keys for the course being evaluated.

    Returns:
        bool: True if a conflict is detected, False otherwise.
    """
    for new in new_times:
        if not new.get('start_time') or not new.get('end_time'):
            continue
        new_start = to_minutes(new['start_time'])
        new_end   = to_minutes(new['end_time'])
        for existing in current_schedule:
            if not existing.get('start_time') or not existing.get('end_time'):
                continue
            if existing['day'] != new['day']:
                continue
            ex_start = to_minutes(existing['start_time'])
            ex_end   = to_minutes(existing['end_time'])
            if not (new_start >= ex_end + 30 or new_end <= ex_start - 30):
                return True
    return False