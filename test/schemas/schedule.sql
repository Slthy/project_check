--This table stores the course offerings for each semester, including the instructor, time, location, and capacity. 
--It references the course catalog for course information and the users table for instructor information. The unique constraint makes sure that there are no duplicate course offerings depending on the course, semester, year, and section.
--times table is for  storing the start and end times for courses, which can be referenced in the schedule table to indicate when a course is offered.

CREATE TABLE IF NOT EXISTS c_offering (
    o_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    c_id        INTEGER NOT NULL,
    semester    TEXT    NOT NULL CHECK(semester IN ('Fall', 'Spring', 'Summer')),
    year        INTEGER NOT NULL,
    section     INTEGER NOT NULL DEFAULT 1,
    i_id        INTEGER,                                
    location    TEXT,                         
    capacity    INTEGER,                      
    UNIQUE(c_id, semester, year, section),
    FOREIGN KEY (c_id) REFERENCES c_catalog(c_id),
    FOREIGN KEY (i_id) REFERENCES users(uid)
);

CREATE TABLE IF NOT EXISTS schedule (
    s_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    o_id        INTEGER NOT NULL,
    day         TEXT    NOT NULL CHECK(day IN ('M', 'T', 'W', 'R', 'F')),
    start_time  VARCHAR(5) CHECK (Start_Time LIKE '[0-2][0-9]:[0-5][0-9]')    NOT NULL,             -- 'HH:MM'
    end_time    VARCHAR(5) CHECK (Start_Time LIKE '[0-2][0-9]:[0-5][0-9]')    NOT NULL,              -- 'HH:MM'
    UNIQUE(o_id, day),
    FOREIGN KEY (o_id) REFERENCES c_offering(o_id)
);