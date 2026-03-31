"""
Shared utility functions used across all blueprints.
"""

import sqlite3
import os

def get_db_connection():
    """
    Open and return a connection to the SQLite database.

    The database path is resolved relative to this file's location,
    two directories up (i.e., the project root). The connection uses
    sqlite3.Row as its row factory so columns are accessible by name.

    Returns:
        sqlite3.Connection: An open database connection.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', '..', 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def has_time_conflict(current_schedule, new_times):
    """
    Determine whether a set of new course times conflicts with an existing schedule.

    Two time slots conflict if they share the same day and do not have at least
    a 30-minute gap between them (i.e., one must end at least 30 minutes before
    the other begins).

    Args:
        current_schedule (list[sqlite3.Row]): Rows containing 'day', 'start_time',
            and 'end_time' for each currently enrolled course.
        new_times (list[sqlite3.Row | dict]): Rows or dicts with the same keys
            for the course being evaluated.

    Returns:
        bool: True if a conflict is detected, False otherwise.
    """
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

def to_minutes(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m