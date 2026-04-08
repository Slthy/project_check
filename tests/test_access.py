from datetime import timedelta
from utils.functions import to_minutes, has_time_conflict

def test_to_minutes():
    """Test that time conversions work perfectly."""
    assert to_minutes("15:30") == 930
    assert to_minutes("08:00") == 480
    
    td = timedelta(hours=14, minutes=15)
    assert to_minutes(td) == 855

def test_has_time_conflict():
    """Test the 30-minute gap schedule conflict logic."""
    current_schedule = [{'day': 'M', 'start_time': '10:00', 'end_time': '11:00'}]
    
    new_class_1 = [{'day': 'M', 'start_time': '11:00', 'end_time': '12:00'}]
    assert has_time_conflict(current_schedule, new_class_1) == True

    new_class_2 = [{'day': 'M', 'start_time': '11:30', 'end_time': '12:30'}]
    assert has_time_conflict(current_schedule, new_class_2) == False

    new_class_3 = [{'day': 'T', 'start_time': '10:00', 'end_time': '11:00'}]
    assert has_time_conflict(current_schedule, new_class_3) == False