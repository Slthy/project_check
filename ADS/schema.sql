CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS programs (
    program_id INT AUTO_INCREMENT PRIMARY KEY,
    program_code VARCHAR(10) NOT NULL UNIQUE,
    program_name VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_code VARCHAR(10) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS terms (
    term_id INT AUTO_INCREMENT PRIMARY KEY,
    term_name VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    grade_code VARCHAR(5) NOT NULL UNIQUE,
    grade_points DECIMAL(3, 2) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role_id INT NOT NULL,
    CONSTRAINT fk_users_role FOREIGN KEY (role_id) REFERENCES roles (role_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_faculty_user FOREIGN KEY (user_id) REFERENCES users (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS system_administrators (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    CONSTRAINT fk_admin_user FOREIGN KEY (user_id) REFERENCES users (user_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    uid CHAR(8) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    email VARCHAR(255),
    program_id INT NOT NULL,
    faculty_id INT,
    CONSTRAINT fk_students_user FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT fk_students_program FOREIGN KEY (program_id) REFERENCES programs (program_id),
    CONSTRAINT fk_students_faculty FOREIGN KEY (faculty_id) REFERENCES faculty (faculty_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS alumni (
    alumni_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    uid CHAR(8) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    email VARCHAR(255),
    program_id INT NOT NULL,
    graduation_term_id INT NOT NULL,
    graduation_year INT NOT NULL,
    final_gpa DECIMAL(3, 2) NOT NULL,
    CONSTRAINT fk_alumni_user FOREIGN KEY (user_id) REFERENCES users (user_id),
    CONSTRAINT fk_alumni_program FOREIGN KEY (program_id) REFERENCES programs (program_id),
    CONSTRAINT fk_alumni_term FOREIGN KEY (graduation_term_id) REFERENCES terms (term_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    course_number VARCHAR(10) NOT NULL,
    title VARCHAR(255) NOT NULL,
    credit_hours INT NOT NULL,
    UNIQUE KEY uq_courses_dept_number (department_id, course_number),
    CONSTRAINT fk_courses_department FOREIGN KEY (department_id) REFERENCES departments (department_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS course_prerequisites (
    course_id INT NOT NULL,
    prerequisite_course_id INT NOT NULL,
    PRIMARY KEY (course_id, prerequisite_course_id),
    CONSTRAINT fk_prereq_course FOREIGN KEY (course_id) REFERENCES courses (course_id),
    CONSTRAINT fk_prereq_required FOREIGN KEY (prerequisite_course_id) REFERENCES courses (course_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS program_requirement (
    program_id INT PRIMARY KEY,
    min_gpa DECIMAL(3, 2) NOT NULL,
    min_total_credits INT NOT NULL,
    max_non_cs_courses INT NOT NULL,
    max_non_cs_credits INT NOT NULL,
    max_grade_below_b INT NOT NULL,
    CONSTRAINT fk_program_req_program FOREIGN KEY (program_id) REFERENCES programs (program_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS program_required_courses (
    program_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (program_id, course_id),
    CONSTRAINT fk_program_required_program FOREIGN KEY (program_id) REFERENCES programs (program_id),
    CONSTRAINT fk_program_required_course FOREIGN KEY (course_id) REFERENCES courses (course_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS student_enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    term_id INT NOT NULL,
    year_taken INT NOT NULL,
    grade_id INT NOT NULL,
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id) REFERENCES students (student_id),
    CONSTRAINT fk_enrollments_course FOREIGN KEY (course_id) REFERENCES courses (course_id),
    CONSTRAINT fk_enrollments_term FOREIGN KEY (term_id) REFERENCES terms (term_id),
    CONSTRAINT fk_enrollments_grade FOREIGN KEY (grade_id) REFERENCES grades (grade_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS form1 (
    form1_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    audit_passed TINYINT(1) NOT NULL DEFAULT 0,
    advisor_decision ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_form1_student FOREIGN KEY (student_id) REFERENCES students (student_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS form1_courses (
    form1_id INT NOT NULL,
    course_id INT NOT NULL,
    PRIMARY KEY (form1_id, course_id),
    CONSTRAINT fk_form1_courses_form1 FOREIGN KEY (form1_id) REFERENCES form1 (form1_id),
    CONSTRAINT fk_form1_courses_course FOREIGN KEY (course_id) REFERENCES courses (course_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS graduation_applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    form1_id INT NOT NULL,
    audit_passed TINYINT(1) NOT NULL DEFAULT 0,
    gs_decision ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_grad_app_student FOREIGN KEY (student_id) REFERENCES students (student_id),
    CONSTRAINT fk_grad_app_form1 FOREIGN KEY (form1_id) REFERENCES form1 (form1_id)
) ENGINE=InnoDB;

INSERT IGNORE INTO roles (role_name) VALUES
    ('admin'),
    ('grad_secretary'),
    ('advisor'),
    ('student'),
    ('alumni');

INSERT IGNORE INTO programs (program_code, program_name) VALUES
    ('MS', 'Master of Science in Computer Science'),
    ('PhD', 'Doctor of Philosophy in Computer Science');

INSERT IGNORE INTO departments (department_code) VALUES
    ('CSCI'),
    ('ECE'),
    ('MATH');

INSERT IGNORE INTO terms (term_name) VALUES
    ('Fall'),
    ('Spring'),
    ('Summer');

INSERT IGNORE INTO grades (grade_code, grade_points) VALUES
    ('A', 4.00),
    ('A-', 3.70),
    ('B+', 3.30),
    ('B', 3.00),
    ('B-', 2.70),
    ('C+', 2.30),
    ('C', 2.00),
    ('F', 0.00),
    ('IP', 0.00);

INSERT IGNORE INTO program_requirement (
    program_id,
    min_gpa,
    min_total_credits,
    max_non_cs_courses,
    max_non_cs_credits,
    max_grade_below_b,
)
SELECT p.program_id, 3.00, 30, 2, 6, 2
FROM programs p
WHERE p.program_code = 'MS';

INSERT IGNORE INTO program_requirement (
    program_id,
    min_gpa,
    min_total_credits,
    max_non_cs_courses,
    max_non_cs_credits,
    max_grade_below_b,
)
SELECT p.program_id, 3.50, 36, 999, 2997, 1
FROM programs p
WHERE p.program_code = 'PhD';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'admin1', '$2b$12$TUnJTOloSkbkeio/tSvik.zuO8o3K2XM0LRPRoHVmzJWL4D8utFEu', role_id
FROM roles
WHERE role_name = 'admin';

INSERT IGNORE INTO system_administrators (
    user_id,
    first_name,
    last_name
)
SELECT user_id, 'System', 'Admin'
FROM users
WHERE username = 'admin1';

INSERT IGNORE INTO courses (
    department_id,
    course_number,
    title,
    credit_hours
)
SELECT d.department_id, c.course_number, c.title, c.credit_hours
FROM (
    SELECT 'CSCI' AS dept_code, '6221' AS course_number, 'SW Paradigms' AS title, 3 AS credit_hours
    UNION ALL SELECT 'CSCI', '6461', 'Computer Architecture', 3
    UNION ALL SELECT 'CSCI', '6212', 'Algorithms', 3
    UNION ALL SELECT 'CSCI', '6220', 'Machine Learning', 3
    UNION ALL SELECT 'CSCI', '6232', 'Networks 1', 3
    UNION ALL SELECT 'CSCI', '6233', 'Networks 2', 3
    UNION ALL SELECT 'CSCI', '6241', 'Database 1', 3
    UNION ALL SELECT 'CSCI', '6242', 'Database 2', 3
    UNION ALL SELECT 'CSCI', '6246', 'Compilers', 3
    UNION ALL SELECT 'CSCI', '6260', 'Multimedia', 3
    UNION ALL SELECT 'CSCI', '6251', 'Cloud Computing', 3
    UNION ALL SELECT 'CSCI', '6254', 'SW Engineering', 3
    UNION ALL SELECT 'CSCI', '6262', 'Graphics 1', 3
    UNION ALL SELECT 'CSCI', '6283', 'Security 1', 3
    UNION ALL SELECT 'CSCI', '6284', 'Cryptography', 3
    UNION ALL SELECT 'CSCI', '6286', 'Network Security', 3
    UNION ALL SELECT 'CSCI', '6325', 'Algorithms 2', 3
    UNION ALL SELECT 'CSCI', '6339', 'Embedded Systems', 3
    UNION ALL SELECT 'CSCI', '6384', 'Cryptography 2', 3
    UNION ALL SELECT 'ECE', '6241', 'Communication Theory', 3
    UNION ALL SELECT 'ECE', '6242', 'Information Theory 2', 3
    UNION ALL SELECT 'MATH', '6210', 'Logic 2', 3
) c
JOIN departments d ON d.department_code = c.dept_code;

INSERT IGNORE INTO course_prerequisites (
    course_id,
    prerequisite_course_id
)
SELECT target_course.course_id, required_course.course_id
FROM (
    SELECT 'CSCI' AS target_dept, '6233' AS target_course, 'CSCI' AS required_dept, '6232' AS required_course
    UNION ALL SELECT 'CSCI', '6242', 'CSCI', '6241'
    UNION ALL SELECT 'CSCI', '6246', 'CSCI', '6461'
    UNION ALL SELECT 'CSCI', '6246', 'CSCI', '6212'
    UNION ALL SELECT 'CSCI', '6251', 'CSCI', '6461'
    UNION ALL SELECT 'CSCI', '6254', 'CSCI', '6221'
    UNION ALL SELECT 'CSCI', '6283', 'CSCI', '6212'
    UNION ALL SELECT 'CSCI', '6284', 'CSCI', '6212'
    UNION ALL SELECT 'CSCI', '6286', 'CSCI', '6283'
    UNION ALL SELECT 'CSCI', '6286', 'CSCI', '6232'
    UNION ALL SELECT 'CSCI', '6325', 'CSCI', '6212'
    UNION ALL SELECT 'CSCI', '6339', 'CSCI', '6461'
    UNION ALL SELECT 'CSCI', '6339', 'CSCI', '6212'
    UNION ALL SELECT 'CSCI', '6384', 'CSCI', '6284'
) pr
JOIN departments target_dept ON target_dept.department_code = pr.target_dept
JOIN courses target_course ON target_course.department_id = target_dept.department_id
    AND target_course.course_number = pr.target_course
JOIN departments required_dept ON required_dept.department_code = pr.required_dept
JOIN courses required_course ON required_course.department_id = required_dept.department_id
    AND required_course.course_number = pr.required_course;

INSERT IGNORE INTO program_required_courses (program_id, course_id)
SELECT p.program_id, c.course_id
FROM (
    SELECT 'MS' AS program_code, 'CSCI' AS dept_code, '6212' AS course_number
    UNION ALL SELECT 'MS', 'CSCI', '6221'
    UNION ALL SELECT 'MS', 'CSCI', '6461'
) r
JOIN programs p ON p.program_code = r.program_code
JOIN departments d ON d.department_code = r.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = r.course_number;

-- Required project accounts and seed records.
INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'gs_office', '$2b$12$3sICyD7Ca/l9b8BPcgiL5egq13FXJBov8qoXM5kWGAna2cKg3HZ4W', role_id
FROM roles
WHERE role_name = 'grad_secretary';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'narahari', '$2b$12$rEo.K4oqmhewDNa1SZxPnuQRjySTkw8ltPH8.a7E5JPdTpn5M8Pzu', role_id
FROM roles
WHERE role_name = 'advisor';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'parmer', '$2b$12$C8tV2oNLR8vcYrtmuB/sqeEwqpdBr7T.7eNnpwK/zryMl4.yLPkmO', role_id
FROM roles
WHERE role_name = 'advisor';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'pmccartney', '$2b$12$2L/CiOsVMm8j6ZkbNIWq0egZ4mbTbOIXMuEgMRRlUM3HBAnyrfra6', role_id
FROM roles
WHERE role_name = 'student';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'gharrison', '$2b$12$/rDDIwWnvlXqbJftuS9gBewoCBcPFg147OBuZwRF3Ue9bkAJV21z.', role_id
FROM roles
WHERE role_name = 'student';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'rstarr', '$2b$12$jEu/ZFKmi9J0d7UIdp/NB.tp0YO1JRQXtZNSvJJPA0rGWNOdIs4Fq', role_id
FROM roles
WHERE role_name = 'student';

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'eclapton', '$2b$12$eq9ocvcSUumUmo.8YGOZPuhVOPAlwD3rDmF3SDtExArzldywp0AUu', role_id
FROM roles
WHERE role_name = 'alumni';

INSERT IGNORE INTO faculty (
    user_id,
    first_name,
    last_name
)
SELECT user_id, 'Sridhar', 'Narahari'
FROM users
WHERE username = 'narahari';

INSERT IGNORE INTO faculty (
    user_id,
    first_name,
    last_name
)
SELECT user_id, 'John', 'Parmer'
FROM users
WHERE username = 'parmer';

INSERT IGNORE INTO students (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    faculty_id
)
SELECT u.user_id, '55555555', 'Paul', 'McCartney', '1 Abbey Rd', 'paul.mccartney@gwu.edu', p.program_id, f.faculty_id
FROM users u
JOIN programs p ON p.program_code = 'MS'
LEFT JOIN faculty f ON f.user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'narahari'
)
WHERE u.username = 'pmccartney';

INSERT IGNORE INTO students (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    faculty_id
)
SELECT u.user_id, '66666666', 'George', 'Harrison', '2 Abbey Rd', 'george.harrison@gwu.edu', p.program_id, f.faculty_id
FROM users u
JOIN programs p ON p.program_code = 'MS'
LEFT JOIN faculty f ON f.user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'parmer'
)
WHERE u.username = 'gharrison';

INSERT IGNORE INTO students (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    faculty_id
)
SELECT u.user_id, '88888888', 'Ringo', 'Starr', '3 Abbey Rd', 'ringo.starr@gwu.edu', p.program_id, f.faculty_id
FROM users u
JOIN programs p ON p.program_code = 'PhD'
LEFT JOIN faculty f ON f.user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'parmer'
)
WHERE u.username = 'rstarr';

INSERT IGNORE INTO students (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    faculty_id
)
SELECT u.user_id, '77777777', 'Eric', 'Clapton', '4 Abbey Rd', 'eric.clapton@gwu.edu', p.program_id, f.faculty_id
FROM users u
JOIN programs p ON p.program_code = 'MS'
LEFT JOIN faculty f ON f.user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'narahari'
)
WHERE u.username = 'eclapton';

INSERT IGNORE INTO alumni (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    graduation_term_id,
    graduation_year,
    final_gpa
)
SELECT u.user_id, '77777777', 'Eric', 'Clapton', '4 Abbey Rd', 'eric.clapton@gwu.edu', p.program_id, t.term_id, 2014, 3.30
FROM users u
JOIN programs p ON p.program_code = 'MS'
JOIN terms t ON t.term_name = 'Spring'
WHERE u.username = 'eclapton';

INSERT IGNORE INTO student_enrollments (
    student_id,
    course_id,
    term_id,
    year_taken,
    grade_id
)
SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
FROM (
    SELECT 'pmccartney' AS username, 'CSCI' AS dept_code, '6221' AS course_number, 'Fall' AS term_name, 2021 AS year_taken, 'A' AS grade_code
    UNION ALL SELECT 'pmccartney', 'CSCI', '6212', 'Spring', 2022, 'A'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6461', 'Summer', 2022, 'A'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6232', 'Fall', 2022, 'A'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6233', 'Spring', 2023, 'A'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6241', 'Summer', 2023, 'B'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6246', 'Fall', 2023, 'B'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6262', 'Spring', 2024, 'B'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6283', 'Summer', 2024, 'B'
    UNION ALL SELECT 'pmccartney', 'CSCI', '6242', 'Fall', 2024, 'B'
) e
JOIN users u ON u.username = e.username
JOIN students s ON s.user_id = u.user_id
JOIN departments d ON d.department_code = e.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = e.course_number
JOIN terms t ON t.term_name = e.term_name
JOIN grades g ON g.grade_code = e.grade_code;

INSERT IGNORE INTO student_enrollments (
    student_id,
    course_id,
    term_id,
    year_taken,
    grade_id
)
SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
FROM (
    SELECT 'gharrison' AS username, 'ECE' AS dept_code, '6242' AS course_number, 'Fall' AS term_name, 2021 AS year_taken, 'C' AS grade_code
    UNION ALL SELECT 'gharrison', 'CSCI', '6221', 'Spring', 2022, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6461', 'Summer', 2022, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6212', 'Fall', 2022, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6232', 'Spring', 2023, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6233', 'Summer', 2023, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6241', 'Fall', 2023, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6242', 'Spring', 2024, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6283', 'Summer', 2024, 'B'
    UNION ALL SELECT 'gharrison', 'CSCI', '6284', 'Fall', 2024, 'B'
) e
JOIN users u ON u.username = e.username
JOIN students s ON s.user_id = u.user_id
JOIN departments d ON d.department_code = e.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = e.course_number
JOIN terms t ON t.term_name = e.term_name
JOIN grades g ON g.grade_code = e.grade_code;

INSERT IGNORE INTO student_enrollments (
    student_id,
    course_id,
    term_id,
    year_taken,
    grade_id
)
SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
FROM (
    SELECT 'rstarr' AS username, 'CSCI' AS dept_code, '6212' AS course_number, 'Fall' AS term_name, 2020 AS year_taken, 'A' AS grade_code
    UNION ALL SELECT 'rstarr', 'CSCI', '6221', 'Spring', 2021, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6461', 'Summer', 2021, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6232', 'Fall', 2021, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6233', 'Spring', 2022, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6241', 'Summer', 2022, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6242', 'Fall', 2022, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6246', 'Spring', 2023, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6262', 'Summer', 2023, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6283', 'Fall', 2023, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6284', 'Spring', 2024, 'A'
    UNION ALL SELECT 'rstarr', 'CSCI', '6286', 'Summer', 2024, 'A'
) e
JOIN users u ON u.username = e.username
JOIN students s ON s.user_id = u.user_id
JOIN departments d ON d.department_code = e.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = e.course_number
JOIN terms t ON t.term_name = e.term_name
JOIN grades g ON g.grade_code = e.grade_code;

INSERT IGNORE INTO student_enrollments (
    student_id,
    course_id,
    term_id,
    year_taken,
    grade_id
)
SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
FROM (
    SELECT 'eclapton' AS username, 'CSCI' AS dept_code, '6221' AS course_number, 'Fall' AS term_name, 2011 AS year_taken, 'B' AS grade_code
    UNION ALL SELECT 'eclapton', 'CSCI', '6212', 'Spring', 2012, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6461', 'Summer', 2012, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6232', 'Fall', 2012, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6233', 'Spring', 2013, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6241', 'Summer', 2013, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6242', 'Fall', 2013, 'B'
    UNION ALL SELECT 'eclapton', 'CSCI', '6283', 'Spring', 2014, 'A'
    UNION ALL SELECT 'eclapton', 'CSCI', '6284', 'Spring', 2014, 'A'
    UNION ALL SELECT 'eclapton', 'CSCI', '6286', 'Spring', 2014, 'A'
) e
JOIN users u ON u.username = e.username
JOIN students s ON s.user_id = u.user_id
JOIN departments d ON d.department_code = e.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = e.course_number
JOIN terms t ON t.term_name = e.term_name
JOIN grades g ON g.grade_code = e.grade_code;

INSERT IGNORE INTO users (
    username,
    password_hash,
    role_id
)
SELECT 'phd1', 'phdpass', role_id
FROM roles
WHERE role_name = 'student';

INSERT IGNORE INTO students (
    user_id,
    uid,
    first_name,
    last_name,
    address,
    email,
    program_id,
    faculty_id
)
SELECT u.user_id, '23456789', 'Phd', 'Student', '100 Research Ln', 'phd1@gwu.edu', p.program_id, f.faculty_id
FROM users u
JOIN programs p ON p.program_code = 'PhD'
LEFT JOIN faculty f ON f.user_id = (
    SELECT user_id
    FROM users
    WHERE username = 'advisor1'
)
WHERE u.username = 'phd1';

INSERT IGNORE INTO student_enrollments (
    student_id,
    course_id,
    term_id,
    year_taken,
    grade_id
)
SELECT s.student_id, c.course_id, t.term_id, e.year_taken, g.grade_id
FROM (
    SELECT 'phd1' AS username, 'CSCI' AS dept_code, '6212' AS course_number, 'Fall' AS term_name, 2023 AS year_taken, 'A-' AS grade_code
    UNION ALL SELECT 'phd1', 'CSCI', '6241', 'Spring', 2024, 'B+'
    UNION ALL SELECT 'phd1', 'CSCI', '6283', 'Summer', 2024, 'A'
    UNION ALL SELECT 'phd1', 'ECE', '6242', 'Fall', 2025, 'B'
    UNION ALL SELECT 'phd1', 'MATH', '6210', 'Spring', 2025, 'A-'
) e
JOIN users u ON u.username = e.username
JOIN students s ON s.user_id = u.user_id
JOIN departments d ON d.department_code = e.dept_code
JOIN courses c ON c.department_id = d.department_id
    AND c.course_number = e.course_number
JOIN terms t ON t.term_name = e.term_name
JOIN grades g ON g.grade_code = e.grade_code;
