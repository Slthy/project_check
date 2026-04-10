## Schema Documentation

The APPS database is organized around the admissions workflow: managing user accounts, applicant/application data, supporting materials, faculty review, and final admission outcome.

### Core Tables

- `roles(rnumber, rtitle)`: lookup table for roles: Applicant (`0`), Student (`1`), Faculty Reviewer (`2`), GS (`3`), CAC (`4`), Admin (`5`).
- `users(user_id, email, password, role_id)`: login/account information for all users.
- `departments(dnumber, dname)`: academic departments.
- `programs(pnumber, pname, dno)`: graduate programs; each program belongs to one department.
- `soughtdeg(deg_no, deg_type)`: lookup table for degree sought (`MS`, `PHD`).

### Applicant and Application Tables

- `applicants(uid, user_id, fname, lname, address, dob, ssn)`: personal data for applicants. `uid` is the university/applicant identifier and is different from `user_id`. `uid` is initialized only for applicants when they start an application, while `user_id` exists for every role.
- `applications(app_id, uid, deg_no, pro_no, semester, app_year, status, final_dec, toefl_score, toefl_exam_year, areas_of_interest)`: main application record linked to one applicant, one degree sought, and one program.

### Supporting Application Material

- `workex(wid, app_id, job_title, description, com_name, man_name, man_email, man_number, start_date, end_date)`: applicant work experience.
- `previous_deg(deg_id, app_id, dtype, dyear, dGPA, duni, dmajor)`: prior degrees for an application.
- `recommendation(rid, app_id, rfname, rlname, remail, rnumber, raffiliation, rtitle, submitted, submitted_date, letter_text, letter_rating, is_generic, is_credible)`: recommendation request and submission data, plus reviewer evaluation of the letter.
- `transcripts(trans_id, app_id, received, received_date)`: transcript tracking.
- `gre(gid, app_id, verbal, quantitative, total, subj_score, subj_name, exam_year)`: GRE data.

### Review and Decision Tables

- `faculty(user_id, fname, lname, dno)`: faculty members, including reviewers and CAC. GS is not modeled as faculty.
- `review(review_id, app_id, reviewer_id, rating, recom_advisor_id, comments, reject_reason, deficiency_courses, final_recommendation)`: faculty review data for an application.
- `students(uid, user_id, admit_app_id, start_semester, start_year)`: admitted applicants who become students.
- `password_reset_requests(req_id, user_id, requested_date, status)`: password reset workflow.

### Relationships

- One user has one role.
- One applicant corresponds to one user.
- One applicant can have multiple applications.
- Each application belongs to one program and one degree type.
- Each application can have multiple `previous_deg`, `workex`, `recommendation`, and `review` rows.
- `review.reviewer_id` and `review.recom_advisor_id` both reference `faculty`.
- An admitted application may produce one student record.

## Normalization

The schema is mostly in **3NF**, with the main exception being `recommendation`.

- **1NF**: Attributes are atomic; repeating groups are moved into separate tables such as `previous_deg`, `workex`, `recommendation`, and `review`.
- **2NF**: Non-key attributes depend on the full primary key because each table uses a single-column primary key.
- **3NF**: A table is in 3NF if every non-key attribute depends on the primary key, and non-key attributes do not depend on other non-key attributes.

Lookup/reference data is separated into:
- `roles`
- `departments`
- `programs`
- `soughtdeg`

### Note on `recommendation`

The `recommendation` table stores both:
- recommendation request/submission data
- evaluation data about that recommendation letter

This combines two related but different concepts in one table, which is the main reason it is the least normalized part of the schema.

## Corrections / Clarifications

- `applications` does **not** contain foreign keys to supporting material tables. It is the other way around: `workex`, `previous_deg`, `recommendation`, `transcripts`, `gre`, and `review` reference `applications`.
- The schema uses transcript and GRE as one-per-application in practice.
- The schema treats faculty as including CAC, but GS is not a faculty member.

### Possible Sources of Confusion

**`user_id` vs `uid`**
- `user_id` is the login/account id for any system user.
- `uid` is the applicant/student university identifier.

**Student role vs Applicant role**
- `Applicant` is someone currently applying.
- `Student` is an admitted applicant.
    - When an applicant is admitted, the original applicant account remains unchanged so the user can still log in as an applicant and see an admitted status with a congratulations message. A separate student account is then created and linked in the students table, allowing the admitted applicant to also exist as a student without replacing the original applicant record. This student account will have an assigned username and password.

**`recommendation` table**
- `recommendation` stores both the request/submission and the evaluation of that letter.

**`status` vs `final_dec` in `applications`**
- `status` tracks workflow state.
- `final_dec` stores the committee outcome.

## Outside Libraries Used

- `Werkzeug.security`: password hashing/checking
- `mysql.connector`: imported in the codebase for MySQL compatibility and future deployment