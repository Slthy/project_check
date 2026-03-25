CREATE TABLE IF NOT EXISTS course_sections (
    section_id INTEGER PRIMARY KEY AUTOINCREMENT,
    c_id INTEGER NOT NULL,
    instructor_id INTEGER NOT NULL,
    semester TEXT NOT NULL,
    year INTEGER NOT NULL,
    day TEXT NOT NULL,
    time TEXT NOT NULL,
    
    FOREIGN KEY (c_id) REFERENCES c_catalog(c_id),
    FOREIGN KEY (instructor_id) REFERENCES users(id)
);