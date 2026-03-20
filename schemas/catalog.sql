-- Course catalog: stores all courses offered by the university
-- The dept and number must be unique and supports up to 2 prerequisites per course, which are self-referential foreign keys to the same table. 

CREATE TABLE IF NOT EXISTS c_catalog (
    c_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    dept        TEXT    NOT NULL,
    number      INTEGER NOT NULL,
    name        TEXT    NOT NULL,
    credits     INTEGER NOT NULL,
    description TEXT,
    prereq1_id  INTEGER,
    prereq2_id  INTEGER,
    UNIQUE(dept, number),
    FOREIGN KEY (prereq1_id) REFERENCES c_catalog(c_id),
    FOREIGN KEY (prereq2_id) REFERENCES c_catalog(c_id)
);