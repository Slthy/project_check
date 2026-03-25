PRAGMA foreign_keys = ON;

INSERT INTO plan (owner_id, is_approved) VALUES
(12345678, 1),
(87654321, 1);

INSERT INTO enrollment (plan_id, o_id, grade) VALUES
(1, 1,  'IP'),
(1, 3,  'B+'),
(1, 5,  'IP'),
(2, 4,  'IP'),
(2, 13, 'A'),
(2, 15, 'IP');