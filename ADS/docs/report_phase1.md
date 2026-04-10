# Phase I Report

## Entity-Relation Diagram

> Please provide an ER diagram for your DB organization.

![image](static/images/ERD.png)

## DB Organization

> Please provide documentation for your chosen data-base schema, including a discussion of the normalization levels.


Our Tables:

- `roles`: stores allowed system roles.
- `programs`: stores degree programs (MS/PhD).
- `departments`: stores academic departments.
- `terms`: stores academic terms (Fall/Spring/Summer).
- `grades`: stores grade codes and grade points.
- `application_status`: stores common workflow statuses (pending/approved/rejected).
- `users`: stores login account data and links each account to a role.
- `faculty`: stores advisor/GS profile data tied to user accounts.
- `system_administrators`: stores admin profile data tied to user accounts.
- `students`: stores active student profile data, program, and advisor assignment.
- `alumni`: stores graduated student summary/profile data.
- `courses`: stores the course catalog (dept, number, title, credits).
- `course_prerequisites`: maps courses to their prerequisite courses.
- `program_requirement`: stores degree-level audit rules (GPA, credits, limits) per program.
- `program_required_courses`: stores required courses for each program.
- `student_enrollments`: stores transcript history (courses, term/year, grade) per student.
- `form1`: stores each student’s latest study plan submission state and advisor decision.
- `form1_courses`: stores course selections attached to a Form 1.
- `graduation_applications`: stores graduation application state and GS decision.

In terms of normalization, the design is generally in 3NF: attributes are atomic (1NF), composite-key tables only store fully dependent data (2NF), and most transitive dependencies are moved into lookup/reference tables (3NF). Overall, this supports maintainability and clean joins for ADS features.

- Admin: create users across roles, delete users, access admin dashboard.
- Graduate Secretary: assign/unassign advisors, review graduation applications, approve or reject graduation.
- Advisor: view assigned students, view student details/transcripts, review and approve/reject Form 1.
- Student: view/edit profile, view/download transcript, create/edit/audit Form 1, apply for graduation and run graduation audit.
- Alumni: view/edit personal profile, view transcript.

## Testing

> Please detail and document how you test the system. Separately document any unit tests, and manual tests.

# We used manual testing to see how routes act when testing changes, many errors occured while testing and writing the code but with manual testing, we were able to solve these issues and how a project that preforms well. 