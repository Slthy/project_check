import sqlite3

def get_db_connection():
  conn = sqlite3.connect("database.db")
  conn.row_factory = sqlite3.Row
  return conn

def time_to_minutes(time_str):
  hours, minutes = map(int, time_str.split(':'))
  return hours * 60 + minutes

def has_time_conflict(current_schedule, new_course_schedule):
  for new_class in new_course_schedule:
    day = new_class['day']
    new_start = time_to_minutes(new_class['start_time'])
    new_end = time_to_minutes(new_class['end_time'])
    
    for ex_start_str, ex_end_str in current_schedule.get(day, []): # for every tuple of hours in current_schedule day (evaluate empty list if day is not in the dict)
      ex_start = time_to_minutes(ex_start_str)
      ex_end = time_to_minutes(ex_end_str)
      
      ok = (new_end <= ex_start - 30) or (new_start >= ex_end + 30) # constraints: end + 30, start - 30
      
      if not ok:    # lil flip-flop, ugly
        return True
              
  return False