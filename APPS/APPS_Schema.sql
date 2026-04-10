DROP TABLE IF EXISTS roles;
CREATE TABLE roles(
    rnumber INT,
    rtitle VARCHAR(50),
    PRIMARY KEY(rnumber)
);

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN KEY(role_id) REFERENCES roles(rnumber)
);

DROP TABLE IF EXISTS departments;
CREATE TABLE departments(
    dnumber INT,
    dname VARCHAR(50) NOT NULL,
    PRIMARY KEY(dnumber)
);

DROP TABLE IF EXISTS programs;
CREATE TABLE programs(
    pnumber INT,
    pname   VARCHAR(50) NOT NULL,
    dno INT NOT NULL,
    PRIMARY KEY(pnumber),
    FOREIGN KEY(dno) REFERENCES departments(dnumber)
);

DROP TABLE IF EXISTS applicants;
CREATE TABLE applicants(
    uid VARCHAR(50),
    user_id VARCHAR(50) NOT NULL UNIQUE,
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    address VARCHAR(100),
    dob DATE,
    ssn VARCHAR(9),
    PRIMARY KEY(uid),
    FOREIGN kEY(user_id) REFERENCES users(user_id)
);

DROP TABLE IF EXISTS faculty;
CREATE TABLE faculty (
    user_id VARCHAR(50),
    fname VARCHAR(50) NOT NULL,
    lname VARCHAR(50) NOT NULL,
    dno INT NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN kEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(dno) REFERENCES departments(dnumber)
);

DROP TABLE IF EXISTS soughtdeg;
CREATE TABLE soughtdeg( 
    deg_no INT,
    deg_type VARCHAR(50),
    PRIMARY KEY(deg_no)
);

DROP TABLE IF EXISTS applications;
CREATE TABLE applications(
    app_id VARCHAR(50),
    uid VARCHAR(50) NOT NULL,
    deg_no INT NOT NULL,
    pro_no INT NOT NULL,
    semester VARCHAR(50) NOT NULL,
    app_year INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    final_dec VARCHAR(50) ,
    toefl_score INT,
    toefl_exam_year INT,
    areas_of_interest VARCHAR(200),
    PRIMARY KEY(app_id),
    FOREIGN KEY(uid) REFERENCES applicants(uid),
    FOREIGN KEY(deg_no) REFERENCES soughtdeg(deg_no),
    FOREIGN KEY(pro_no) REFERENCES programs(pnumber)
);

DROP TABLE IF EXISTS workex;
CREATE TABLE workex(
    wid VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    job_title VARCHAR(50),
    description TEXT,
    com_name VARCHAR(50),
    man_name VARCHAR(50),
    man_email VARCHAR(50),
    man_number VARCHAR(50),
    start_date DATE,
    end_date DATE,
    PRIMARY KEY(wid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

DROP TABLE IF EXISTS previous_deg;
CREATE TABLE previous_deg(
    deg_id VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    dtype VARCHAR(50),
    dyear INT,
    dGPA DECIMAL(3,2) CHECK (dGPA BETWEEN 0.00 AND 4.00),
    duni VARCHAR(50),
    dmajor VARCHAR(50),
    PRIMARY KEY(deg_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

DROP TABLE IF EXISTS recommendation;
CREATE TABLE recommendation(
    rid VARCHAr(50),
    app_id VARCHAR(50) NOT NULL,
    rfname VARCHAR(50),
    rlname VARCHAR(50),
    remail VARCHAR(50),
    rnumber VARCHAR(50),
    raffiliation VARCHAR(50),
    rtitle VARCHAR(50),
    submitted BOOLEAN DEFAULT FALSE,
    submitted_date Date,
    letter_text TEXT,
    letter_rating INT CHECK (letter_rating BETWEEN 1 AND 5),
    is_generic BOOLEAN,
    is_credible BOOLEAN,
    PRIMARY KEY(rid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

DROP TABLE IF EXISTS transcripts;
CREATE TABLE transcripts(
    trans_id VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    received BOOLEAN DEFAULT FALSE,
    received_date DATE,
    PRIMARY KEY(trans_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

DROP TABLE IF EXISTS gre;
CREATE TABLE gre(
    gid VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    verbal INT,
    quantitative INT,
    total INT,
    subj_score INT,
    subj_name VARCHAR(50),
    exam_year INT,
    PRIMARY KEY(gid),
    FOREIGN KEY(app_id) REFERENCES applications(app_id)
);

DROP TABLE IF EXISTS review;
CREATE TABLE review(
    review_id VARCHAR(50),
    app_id VARCHAR(50) NOT NULL,
    reviewer_id VARCHAR(50) NOT NULL,
    rating INT,
    recom_advisor_id VARCHAR(50),
    comments VARCHAR(200),
    reject_reason VARCHAR(100),
    deficiency_courses VARCHAR(100),
    final_recommendation VARCHAR(100),
    PRIMARY KEY(review_id),
    FOREIGN KEY(app_id) REFERENCES applications(app_id),
    FOREIGN KEY (recom_advisor_id) REFERENCES faculty(user_id),
    FOREIGN KEY(reviewer_id) REFERENCES faculty(user_id)
);

DROP TABLE IF EXISTS students;
CREATE TABLE students(
    uid VARCHAR(50),
    user_id VARCHAR(50) UNIQUE,
    admit_app_id VARCHAR(50) UNIQUE,
    start_semester VARCHAR(50),
    start_year INT,
    PRIMARY KEY(uid),
    FOREIGN KEY(uid) REFERENCES applicants(uid),
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(admit_app_id) REFERENCES applications(app_id)
);

INSERT INTO roles (rnumber, rtitle) VALUES
(0, 'Applicant'),
(1, 'Student'),
(2, 'Faculty Reviewer'),
(3, 'GS'),
(4, 'CAC'),
(5, 'Admin');

DROP TABLE IF EXISTS password_reset_requests;
CREATE TABLE password_reset_requests(
    req_id VARCHAR(50),
    user_id VARCHAR(50) NOT NULL,
    requested_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    PRIMARY KEY(req_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
INSERT INTO users (user_id, email, password, role_id) VALUES
('gs1', 'gs1@gwu.edu', 'password', 3),
('cac1', 'cac1@gwu.edu', 'password', 4),
('Admin1', 'Admin1@gwu.edu', 'password', 5),
('Student1', 'Student1@gwu.edu', 'password', 1),
('prof_cs1', 'prof_cs1@gwu.edu', 'password', 2),
('prof_ece1', 'prof_ece1@gwu.edu', 'password', 2),
('prof_bme1', 'prof_bme1@gwu.edu', 'password', 2),
('prof_ce1', 'prof_ce1@gwu.edu', 'password', 2),
('prof_mce1', 'prof_mce1@gwu.edu', 'password', 2),
('narahari', 'narahari@gwu.edu', 'password', 2),
('wood', 'wood@gwu.edu', 'password', 2),
('heller', 'heller@gwu.edu', 'password', 2),
('testID','testID@gmail.com','password', 0),
('arvin', 'arvin@gmail.com', 'password', 0),
('mohab', 'mohab@gmail.com', 'password', 0),
('jlennon', 'jlennon@gwu.edu', 'password', 0),
('rstarr', 'rstarr@gwu.edu', 'password', 0);

INSERT INTO departments (dnumber, dname) VALUES
(1, 'Computer Science'),
(2, 'Electrical & Computer Engineering'),
(3, 'Biomedical Engineering'),
(4, 'Civil & Environmental Engineering'),
(5, 'Mechanical & Aerospace Engineering');

INSERT INTO programs (pnumber, pname, dno) VALUES
(101, 'MS Computer Science', 1),
(102, 'PhD Computer Science', 1),
(103, 'MS Electrical Engineering', 2),
(104, 'MS Computer Engineering', 2),
(105, 'PhD Electrical & Computer Engineering', 2),
(106, 'MS Biomedical Engineering', 3),
(107, 'PhD Biomedical Engineering', 3),
(108, 'MS Civil Engineering', 4),
(109, 'MS Environmental Engineering', 4),
(110, 'MS Mechanical Engineering', 5),
(111, 'MS Aerospace Engineering', 5),
(112, 'PhD Mechanical & Aerospace Engineering', 5);

INSERT INTO soughtdeg (deg_no, deg_type) VALUES
(1, 'MS'),
(2, 'PHD');

INSERT INTO faculty (user_id, fname, lname, dno) VALUES
('prof_cs1', 'Gabe', 'Parmer', 1),
('prof_ece1', 'Thomas', 'Edison', 2),
('prof_bme1', 'Charles', 'Darwin', 3),
('prof_ce1', 'Bridge', 'Skycraper', 4),
('prof_mce1', 'Stephen', 'Hawking', 5),
('narahari', 'Raghu', 'Narahari', 1),
('wood', 'David', 'Wood', 1),
('heller', 'Myles', 'Heller', 1),
('cac1', 'Grace', 'Hopper', 1);

INSERT INTO applicants (uid, user_id, fname, lname, address, dob, ssn) VALUES
('00000001', 'arvin', 'arvin', 'sarsazi', '2026 Wisconsin Ave, Washington, DC', '1999-07-21', '333445555'),
('12312312', 'jlennon', 'John', 'Lennon', '2511 M St NW, Washington, DC', '1998-10-09', '111111111'),
('66666666', 'rstarr', 'Ringo', 'Starr', '2550 Virginia Ave NW, Washington, DC', '1998-07-07', '222111111');

INSERT INTO applications (app_id, uid, deg_no, pro_no, semester, app_year, status, final_dec, toefl_score, toefl_exam_year, areas_of_interest) VALUES
('APP001', '00000001', 2, 101, 'Fall', 2026, 'Decision Made', 'Admit with Aid' , 110, 2023, 'Machine Learning'),
('APP003', '12312312', 1, 101, 'Fall', 2026, 'Complete', NULL, NULL, NULL, 'Systems'),
('APP004', '66666666', 1, 101, 'Fall', 2026, 'Incomplete', NULL, NULL, NULL, 'Computer Architecture');

INSERT INTO previous_deg (deg_id, app_id, dtype, dyear, dGPA, duni, dmajor) VALUES
('D001', 'APP001', 'BS', 2020, '2.85', 'George Washington University', 'Computer Science'),
('D002', 'APP001', 'MS', 2025, '3.40', 'Stanford University', 'Computer Science'),
('D004', 'APP003', 'BS', 2020, '3.70', 'New York University', 'Computer Science'),
('D005', 'APP004', 'BS', 2019, '3.20', 'University of Liverpool', 'Music Technology');


INSERT INTO recommendation (rid, app_id, rfname, rlname, remail, raffiliation, rtitle, submitted, letter_rating, is_generic, is_credible) VALUES
('R001', 'APP001', 'Reza', 'Malek', 'rmm@gwu.edu', 'George Washington University', 'Professor', TRUE, 3, FALSE, TRUE),
('R003', 'APP003', 'Yoko', 'Ono', 'yono@example.com', 'Columbia University', 'Professor', TRUE, NULL, NULL, NULL),
('R004', 'APP004', 'George', 'Martin', 'gmartin@example.com', 'EMI', 'Producer', FALSE, NULL, NULL, NULL);

INSERT INTO transcripts (trans_id, app_id, received, received_date) VALUES
('T001', 'APP001', TRUE, '2025-12-10'),
('T003', 'APP003', TRUE, '2026-01-10'),
('T004', 'APP004', FALSE, NULL);

INSERT INTO gre (gid, app_id, verbal, quantitative, total, subj_score, subj_name, exam_year) VALUES
('G001', 'APP001', 160, 168, 328, NULL, NULL, 2025);

INSERT INTO review (review_id, app_id, reviewer_id, rating, recom_advisor_id, comments, reject_reason, deficiency_courses, final_recommendation) VALUES
('REV001', 'APP001', 'prof_cs1', 4, 'prof_cs1', 'Strong problem solving skills', NULL, NULL, 'Admit with Aid');

INSERT INTO students (uid, user_id, admit_app_id, start_semester, start_year) VALUES
('00000001', 'arvin', 'APP001', 'Fall', 2026);
