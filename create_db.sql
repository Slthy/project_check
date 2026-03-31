-- ADD `.read schemas/*.sql` for every new schema
-- RUN with `sqlite3 database.db < create_db.sql`

PRAGMA foreign_keys = ON;

.read schemas/users.sql
.read schemas/catalog.sql
.read schemas/schedule.sql
.read schemas/enrollment.sql
--- .read schemas/seed_users.sql
--- .read schemas/seed_catalog.sql
--- .read schemas/seed_offerings.sql
--- .read schemas/seed_enrollment.sql


INSERT INTO users (id, fname, lname, email, password, role) VALUES
(10000001, 'System', 'Admin',     'admin@regs.edu',    '$2b$12$L.cI2ivPf84OBlhc75OgmOhfmsXfsbN2GMqVXhSKTBzk8r8mPzb0C', 0),  
(10000002, 'Grace',  'Secretary', 'gs1@regs.edu',      '$2b$12$AEEkdKf7kdVujNcH0s/Ete9a1xQwXVVWwAxQ387aoQQx5WX9Lfopq', 1),  
(10000003, 'Milos',  'Assistant', 'gs2@regs.edu',      '$2b$12$le1AEN3bpeu31ktT5HGie.iEo.TfgwSQrrolNtnR13gMTnQEMkLiK', 1),  
(10000004, 'Bob',    'Narahari',  'bjohnson@regs.edu', '$2b$12$rYWSO3JsxmGt046/x4LO3.KkFrLwkrLgKZr2rUfXWk2jfhA/Aufq.', 2),  
(10000005, 'Alper',  'Choi',      'achoi@regs.edu',    '$2b$12$ZnahcsSr2THpMWyeDeduX.qILmD1Bqj9UKfNKHyzBKy5yns8AoOci', 2),  
(10000006, 'Alice',  'Faculty1',  'afaculty1@regs.edu','$2b$12$L.cI2ivPf84OBlhc75OgmOhfmsXfsbN2GMqVXhSKTBzk8r8mPzb0C', 2),
(10000007, 'Carlos', 'Faculty2',  'cfaculty2@regs.edu','$2b$12$L.cI2ivPf84OBlhc75OgmOhfmsXfsbN2GMqVXhSKTBzk8r8mPzb0C', 2),
(88888888, 'Billie', 'Holiday',   'jdoe@gwu.edu',      '$2b$12$yxUkDOolLezYRNb1kxlf1.wZ5PI.bq7uSX75xic2lT.Aw69aam0ny', 3),  
(99999999, 'Diana',  'Krall',     'jsmith@gwu.edu',    '$2b$12$Wy4FEx2ZXrJeqQIShMB3OeB61L/wHMy0Xg5j0h/FwGTd2IFvG36f6', 3);  

INSERT INTO stud_type (id, track, admit_year) VALUES
(88888888, 'Masters', 2024),   
(99999999, 'Masters', 2023);   

INSERT INTO addresses (a_id, line_one, city, state, zip, country_code) VALUES
(10000001, '789 Oak Dr',     'Seattle',       'WA', '98101', 'US'),
(10000002, '321 Pine Ln',    'Austin',        'TX', '73301', 'US'),
(10000003, '654 Maple Ct',   'Denver',        'CO', '80201', 'US'),
(10000004, '987 Birch Blvd', 'Boston',        'MA', '02108', 'US'),
(10000005, '159 Cedar Pl',   'Chicago',       'IL', '60601', 'US'),
(10000006, '111 Faculty Dr', 'Washington',    'DC', '20052', 'US'),
(10000007, '222 Faculty Ave','Washington',    'DC', '20052', 'US'),
(88888888, '753 Walnut St',  'New York',      'NY', '10001', 'US'),
(99999999, '852 Spruce Way', 'San Francisco', 'CA', '94105', 'US');

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id) VALUES
('CSCI', 6221, 'SW Paradigms',          3, NULL,    NULL),
('CSCI', 6461, 'Computer Architecture', 3, NULL,    NULL),
('CSCI', 6212, 'Algorithms',            3, NULL,    NULL),
('CSCI', 6210, 'Machine Learning',      3, NULL,    NULL),
('CSCI', 6220, 'Networks 1',            3, NULL,    NULL),
('CSCI', 6233, 'Database 1',            3, NULL,    NULL),
('CSCI', 6246, 'Multimedia',            3, NULL,    NULL),
('CSCI', 6254, 'Graphics 1',            3, NULL,    NULL),
('ECE',  6384, 'Communication Theory',  3, NULL,    NULL),
('ECE',  6241, 'Information Theory',    2, NULL,    NULL),
('MATH', 6242, 'Logic',                 2, NULL,    NULL),
('CSCI', 6232, 'Networks 2',            3, 5,       NULL),
('CSCI', 6241, 'Database 2',            3, 6,       NULL),
('CSCI', 6242, 'Compilers',             3, 2,       NULL),
('CSCI', 6260, 'Cloud Computing',       3, 2,       NULL),
('CSCI', 6251, 'SW Engineering',        3, 1,       NULL),
('CSCI', 6262, 'Security 1',            3, 3,       NULL),
('CSCI', 6283, 'Cryptography',          3, 3,       NULL),
('CSCI', 6325, 'Embedded Systems',      3, 2,       NULL),
('CSCI', 6284, 'Network Security',      3, 18,      12),
('CSCI', 6286, 'Algorithms 2',          3, 12,      18),
('CSCI', 6339, 'Cryptography 2',        3, 20,      NULL);

INSERT INTO c_offering (c_id, semester, year, section, i_id) VALUES
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6221), 'Fall', 2025, 1, 10000003),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6461), 'Fall', 2025, 1, 10000004),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6212), 'Fall', 2025, 1, 10000005),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6232), 'Fall', 2025, 1, 10000003),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6233), 'Fall', 2025, 1, 10000006),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6241), 'Fall', 2025, 1, 10000006),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6242), 'Fall', 2025, 1, 10000007),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6246), 'Fall', 2025, 1, 10000004),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6251), 'Fall', 2025, 1, 10000003),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6254), 'Fall', 2025, 1, 10000005),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6260), 'Fall', 2025, 1, 10000007),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6262), 'Fall', 2025, 1, 10000004),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6283), 'Fall', 2025, 1, 10000005),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6284), 'Fall', 2025, 1, 10000006),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6286), 'Fall', 2025, 1, 10000007),
((SELECT c_id FROM c_catalog WHERE dept='ECE'  AND number=6384), 'Fall', 2025, 1, 10000003),
((SELECT c_id FROM c_catalog WHERE dept='ECE'  AND number=6241), 'Fall', 2025, 1, 10000004),
((SELECT c_id FROM c_catalog WHERE dept='MATH' AND number=6242), 'Fall', 2025, 1, 10000005),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6210), 'Fall', 2025, 1, 10000006),
((SELECT c_id FROM c_catalog WHERE dept='CSCI' AND number=6339), 'Fall', 2025, 1, 10000007);

INSERT INTO schedule (o_id, day, start_time, end_time) VALUES
(1,  'M', '15:00', '17:30'),
(2,  'T', '15:00', '17:30'),
(3,  'W', '15:00', '17:30'),
(4,  'M', '18:00', '20:30'),
(5,  'T', '18:00', '20:30'),
(6,  'W', '18:00', '20:30'),
(7,  'R', '18:00', '20:30'),
(8,  'T', '15:00', '17:30'),
(9,  'M', '18:00', '20:30'),
(10, 'M', '15:00', '17:30'),
(11, 'R', '18:00', '20:30'),
(12, 'W', '18:00', '20:30'),
(13, 'T', '18:00', '20:30'),
(14, 'M', '18:00', '20:30'),
(15, 'W', '18:00', '20:30'),
(16, 'W', '15:00', '17:30'),
(17, 'M', '18:00', '20:30'),
(18, 'T', '18:00', '20:30'),
(19, 'W', '18:00', '20:30'),
(20, 'R', '16:00', '18:30');

INSERT INTO plan (owner_id, is_approved) VALUES
(88888888, 1),
(99999999, 1);

INSERT INTO enrollment (plan_id, o_id, grade) VALUES
(1, 2,  'IP'),
(1, 3,  'IP');

VACUUM;