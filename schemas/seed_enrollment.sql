PRAGMA foreign_keys = ON;

INSERT INTO plan (owner_id, is_approved) VALUES
(88888888, 1),
(99999999, 1);

INSERT INTO enrollment (plan_id, o_id, grade) VALUES
(1, 2,  'IP'),
(1, 3,  'IP');