import pytest
from datetime import timedelta
from utils.functions import to_minutes, has_time_conflict

def test_to_minutes():
    # Test string parsing
    assert to_minutes("14:30") == 870
    assert to_minutes("00:15:00") == 15
    
    # Test timedelta parsing
    td = timedelta(hours=14, minutes=30)
    assert to_minutes(td) == 870

def test_has_time_conflict():
    current_schedule = [{'day': 'M', 'start_time': '10:00:00', 'end_time': '11:00:00'}]
    
    # Same day, overlapping time (10:45 is less than 30 mins after 11:00)
    new_course_conflict = [{'day': 'M', 'start_time': '10:45:00', 'end_time': '11:45:00'}]
    assert has_time_conflict(current_schedule, new_course_conflict) == True
    
    # Same day, valid 30m gap
    new_course_valid = [{'day': 'M', 'start_time': '11:30:00', 'end_time': '12:30:00'}]
    assert has_time_conflict(current_schedule, new_course_valid) == False
    
    # Different day
    new_course_diff_day = [{'day': 'T', 'start_time': '10:00:00', 'end_time': '11:00:00'}]
    assert has_time_conflict(current_schedule, new_course_diff_day) == False