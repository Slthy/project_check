PRAGMA foreign_keys = ON;

INSERT INTO users (uid, fname, lname, email, password, role)
VALUES (10000001, 'System', 'Admin', 'admin@regs.edu', 'CHANGE_ME_HASHED', 0);

INSERT INTO users (uid, fname, lname, email, password, role)
VALUES (10000002, 'Grace', 'Secretary', 'gs@regs.edu', 'CHANGE_ME_HASHED', 1);

INSERT INTO users (uid, fname, lname, email, password, role) VALUES
(10000003, 'Alice',   'Smith',    'asmith@regs.edu',    'CHANGE_ME_HASHED', 2),
(10000004, 'Bob',     'Johnson',  'bjohnson@regs.edu',  'CHANGE_ME_HASHED', 2),
(10000005, 'Carol',   'Williams', 'cwilliams@regs.edu', 'CHANGE_ME_HASHED', 2),
(10000006, 'David',   'Brown',    'dbrown@regs.edu',    'CHANGE_ME_HASHED', 2),
(10000007, 'Eve',     'Davis',    'edavis@regs.edu',    'CHANGE_ME_HASHED', 2);

INSERT INTO users (uid, fname, lname, email, password, role) VALUES
(12345678, 'John',  'Doe',   'jdoe@gwu.edu',  'CHANGE_ME_HASHED', 3),
(87654321, 'Jane',  'Smith', 'jsmith@gwu.edu', 'CHANGE_ME_HASHED', 3);

INSERT INTO stud_type (uid, track, admit_year) VALUES
(12345678, 'Masters', 2024),
(87654321, 'PhD',     2023);

INSERT INTO addresses (a_id, line_one, city, state, zip, country_code) VALUES
(12345678, '123 Main St', 'Washington', 'DC', '20052', 'US'),
(87654321, '456 Elm Ave', 'Washington', 'DC', '20001', 'US');