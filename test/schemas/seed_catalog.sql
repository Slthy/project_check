PRAGMA foreign_keys = ON;

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id) VALUES
('CSCI', 6221, 'SW Paradigms',          3, NULL, NULL),
('CSCI', 6461, 'Computer Architecture', 3, NULL, NULL),
('CSCI', 6212, 'Algorithms',            3, NULL, NULL),
('CSCI', 6210, 'Machine Learning',      3, NULL, NULL),
('CSCI', 6220, 'Networks 1',            3, NULL, NULL),
('CSCI', 6233, 'Database 1',            3, NULL, NULL),
('CSCI', 6246, 'Multimedia',            3, NULL, NULL),
('CSCI', 6254, 'Graphics 1',            3, NULL, NULL),
('ECE',  6384, 'Communication Theory',  3, NULL, NULL),
('ECE',  6241, 'Information Theory',    2, NULL, NULL),
('MATH', 6242, 'Logic',                 2, NULL, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6232, 'Networks 2', 3, 5, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6241, 'Database 2', 3, 6, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6242, 'Compilers', 3, 2, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6260, 'Cloud Computing', 3, 2, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6251, 'SW Engineering', 3, 1, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6262, 'Security 1', 3, 3, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6283, 'Cryptography', 3, 3, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6325, 'Embedded Systems', 3, 2, NULL);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6284, 'Network Security', 3, 18, 12);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6286, 'Algorithms 2', 3, 12, 18);

INSERT INTO c_catalog (dept, number, name, credits, prereq1_id, prereq2_id)
VALUES ('CSCI', 6339, 'Cryptography 2', 3, 20, NULL);