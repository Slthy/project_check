-- Student registration record — one row per student per offering.
-- grade will default to 'IP' for in progress, and will be updated when the course is completed. 
--The UNIQUE keyword makes sure that a student cannot enroll in the same offering more than once.


CREATE TABLE IF NOT EXISTS enrollment (
    enroll_id               INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id                 INTEGER NOT NULL,             
    o_id                    INTEGER NOT NULL,             
    grade                   VARCHAR(2)  DEFAULT 'IP'
                                CHECK(grade IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F', 'IP')),
    enrolled_at             DATETIME    DEFAULT (datetime('now')),
    UNIQUE(plan_id, o_id),

    FOREIGN KEY (plan_id)   REFERENCES plan(plan_id),
    FOREIGN KEY (o_id)      REFERENCES c_offering(o_id)
);

CREATE TABLE IF NOT EXISTS plan (
    plan_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id                INTEGER NOT NULL,
    enrolled_at             DATETIME DEFAULT (datetime('now')),
    is_approved             SMALLINT DEFAULT 0 
                                CHECK(is_approved IN (0, 1)),
                                
    FOREIGN KEY (owner_id)  REFERENCES users(uid)
);