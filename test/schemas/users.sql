--Users table: This handles all system accounts, including- admin, GS, faculty, and students. The role column differentiates between these types of users, with 0 for admin, 1 for GS, 2 for faculty, and students
--Each user has a unique ID
--This handles our authentication and authorization for the system, ensuring that only authorized users can access certain features based on their role.
--Contains the type of student as well, and all the addresses for users


PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    uid          INTEGER PRIMARY KEY CHECK(uid >= 10000000 AND uid <= 99999999) DEFAULT 10000000,
    fname       TEXT    NOT NULL,
    lname       TEXT    NOT NULL,
    mname       TEXT,
    email       TEXT    NOT NULL UNIQUE,
    password    TEXT    NOT NULL,
    role        INTEGER NOT NULL CHECK(role IN (0, 1, 2, 3)),
    created_at  TEXT    DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS stud_type (
    uid         INTEGER PRIMARY KEY,
    track       TEXT    NOT NULL CHECK(track IN ('Masters', 'PhD')),
    admit_year  INTEGER,
    FOREIGN KEY (uid) REFERENCES users(uid)
);

CREATE TABLE IF NOT EXISTS addresses (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    a_id         INTEGER NOT NULL,
    line_one     TEXT    NOT NULL,
    line_two     TEXT,
    city         TEXT,
    state        TEXT,
    zip          TEXT    NOT NULL,
    country_code TEXT    NOT NULL DEFAULT 'US',
    FOREIGN KEY (a_id) REFERENCES users(uid)
);