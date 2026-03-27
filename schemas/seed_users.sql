PRAGMA foreign_keys = ON;

INSERT INTO users (id, fname, lname, email, password, role) VALUES
(10000001, 'System', 'Admin',     'admin@regs.edu',    '$2b$12$L.cI2ivPf84OBlhc75OgmOhfmsXfsbN2GMqVXhSKTBzk8r8mPzb0C', 0),  
    -- psw: psw1
(10000002, 'Grace',  'Secretary', 'gs1@regs.edu',      '$2b$12$AEEkdKf7kdVujNcH0s/Ete9a1xQwXVVWwAxQ387aoQQx5WX9Lfopq', 1),  
    -- psw: psw2
(10000003, 'Milos',  'Assistant',  'gs2@regs.edu',     '$2b$12$le1AEN3bpeu31ktT5HGie.iEo.TfgwSQrrolNtnR13gMTnQEMkLiK', 1),  
    -- psw: psw3
(10000004, 'Bob',    'Narahari',  'bjohnson@regs.edu', '$2b$12$rYWSO3JsxmGt046/x4LO3.KkFrLwkrLgKZr2rUfXWk2jfhA/Aufq.', 2),  
    -- psw: psw4
(10000005, 'Alper',  'Choi',      'achoi@regs.edu',    '$2b$12$ZnahcsSr2THpMWyeDeduX.qILmD1Bqj9UKfNKHyzBKy5yns8AoOci', 2),  
    -- psw: psw5
(88888888, 'Billie', 'Holiday',   'jdoe@gwu.edu',      '$2b$12$yxUkDOolLezYRNb1kxlf1.wZ5PI.bq7uSX75xic2lT.Aw69aam0ny', 3),  
    -- psw: psw6
(99999999, 'Diana',  'Krall',     'jsmith@gwu.edu',    '$2b$12$Wy4FEx2ZXrJeqQIShMB3OeB61L/wHMy0Xg5j0h/FwGTd2IFvG36f6', 3);  
    -- psw: psw7

INSERT INTO stud_type (id, track, admit_year) VALUES
(12345678, 'Masters', 2024),
(87654321, 'Masters', 2023);

INSERT INTO addresses (a_id, line_one, city, state, zip, country_code) VALUES
(12345678, '123 Main St',    'Washington',    'DC', '20052', 'US'),
(87654321, '456 Elm Ave',    'Washington',    'DC', '20001', 'US'),
(10000001, '789 Oak Dr',     'Seattle',       'WA', '98101', 'US'),
(10000002, '321 Pine Ln',    'Austin',        'TX', '73301', 'US'),
(10000003, '654 Maple Ct',   'Denver',        'CO', '80201', 'US'),
(10000004, '987 Birch Blvd', 'Boston',        'MA', '02108', 'US'),
(10000005, '159 Cedar Pl',   'Chicago',       'IL', '60601', 'US'),
(88888888, '753 Walnut St',  'New York',      'NY', '10001', 'US'),
(99999999, '852 Spruce Way', 'San Francisco', 'CA', '94105', 'US');