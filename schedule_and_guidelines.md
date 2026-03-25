# BirdsArentReal - Spring '26 REGS
## Borsato A. — Elsawalhi A. — Parekh V.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Team Roles & Assignments](#team-roles--assignments)
4. [Task Breakdown](#task-breakdown)
5. [Schedule & Milestones](#schedule--milestones)
6. [Database Design Guidelines](#database-design-guidelines)
7. [Coding Guidelines](#coding-guidelines)
8. [Git Workflow](#git-workflow)
9. [Meeting Norms](#meeting-norms)
10. [Phase 2 Forward-Thinking Notes](#phase-2-forward-thinking-notes)

---

## Project Overview

**Course:** CS 2541W  
**Project:** Registration System (REGS) — Phase 1  
**Goal:** Build a web-based graduate course registration system using **MySQL** and **Python Flask**, deployed on the production server.

### Core Functionality (Phase 1)
- Graduate students can create accounts, log in, and register (add/drop) for courses
- Faculty instructors can submit final grades (once, no changes after)
- Grad Secretary (GS) can view/search transcripts and enter or override grades
- Sysadmin can create all user types
- All users can view student transcripts (with IP for in-progress courses)
- Schedule conflict detection on registration
- Prerequisite enforcement on course registration
- Students can update personal information such as address and email

### User Roles Summary
| Role | Create Users | Register Courses | Enter Grades | Change Grades | View Transcripts |
|---|---|---|---|---|---|
| Sysadmin | ✅ | — | — | ✅ | ✅ |
| Grad Secretary | ❌ | — | ✅ | ✅ | ✅ |
| Faculty | ❌ | — | ✅ (once) | ❌ | ✅ |
| Student | ❌ (self-register) | ✅ | — | — | Own only |

> Note: students self-register, while sysadmin can create accounts for any user type if needed.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.x + Flask |
| Database | MySQL |
| Frontend | HTML/CSS + Jinja2 templates (Flask) |
| ORM / DB driver | `mysql-connector-python` or `PyMySQL` |
| Auth | Flask-Login + bcrypt password hashing |

> **Note:** Be conservative with extra libraries — Phase 2 requires integration with other modules. Confirm any non-standard packages with the team before adding.

---

## Team Roles & Assignments

### Ownership Areas (tentative — adjust as needed)

| Area | Owner | Backup |
|---|---|---|
| Database schema & migrations | Borsato A. | Parekh V. |
| Backend / Flask routes & logic | Elsawalhi A. | Borsato A. |
| Frontend / UI templates | Parekh V. | Elsawalhi A. |
| Auth system (login, roles, sessions) | Borsato A. | Elsawalhi A. |
| Documentation & report writing | Elsawalhi A. | Parekh V. |
| Testing & QA | ??? | ??? |


> Each person owns their area end-to-end (schema ↔ route ↔ template for their feature) but should coordinate at interface points. Ownership = accountability, not solo work.

---

## Task Breakdown

### 🗄️ Database (Owner: Borsato A.)

- [ ] Design ER diagram covering all entities and relationships
- [ ] Finalize normalized schema (see [Database Design Guidelines](#database-design-guidelines))
- [ ] Write SQL `CREATE TABLE` scripts with all constraints
- [ ] Seed script: populate course catalog from Appendix A (21 courses, all prereqs)
- [ ] Seed script: populate course schedule from Appendix A (20 scheduled sections)
- [ ] Seed script: create default sysadmin account
- [ ] Verify foreign key constraints and cascade behaviors

**Key tables to design (at minimum):**
`users`, `students`, `faculty`, `grad_secretary`, `course_catalog`, `schedule`, `enrollment`

---

### 🔧 Backend / Flask Routes (Owner: Elsawalhi A.)

**Auth routes:**
- [ ] `POST /register` — student self-registration
- [ ] `POST /login` — all user types
- [ ] `POST /logout`

**Student routes:**
- [ ] `GET /courses` — browse available courses (with prereq/conflict status)
- [ ] `POST /courses/add` — enroll in a course (check prereqs + schedule conflicts)
- [ ] `POST /courses/drop` — drop a course
- [ ] `GET /transcript` — view own transcript
- [ ] `POST /profile/update` — update personal info (address, email)

**Faculty routes:**
- [ ] `GET /faculty/courses` — view courses they teach
- [ ] POST /faculty/grades — submit final grade for assigned students only (locked after submit)

**GS routes:**
- [ ] GET /gs/transcripts — search and view any student transcript
- [ ] `POST /gs/grades` — enter or override any grade

**Sysadmin routes:**
- [ ] POST /admin/create-user — create faculty, GS, and student accounts as needed

**Business logic (shared helpers):**
- [ ] Prerequisite checker: student has passing grade in all prereqs
- [ ] Schedule conflict checker: no two enrolled courses overlap (allow 30-min gap)
- [ ] PhD restriction: PhD students can only register for 6000-level courses
- [ ] Grade lock: faculty cannot change grade once submitted

---

### 🎨 Frontend / UI (Owner: Parekh V.)

- [ ] Base layout template with nav (role-aware links)
- [ ] Login / registration forms with validation
- [ ] Course browser (table with prereq status, time, day)
- [ ] Add/Drop confirmation modals
- [ ] Transcript view (table: course, semester, grade — IP if in progress)
- [ ] Faculty grade entry form
- [ ] GS student search + grade override form
- [ ] Sysadmin user creation form
- [ ] Flash messages for errors and success (conflict detected, prereq not met, etc.)
- [ ] Basic responsive styling

**UI must-haves per spec:**
- Input form validation (client-side + server-side)
- Clear error messaging (schedule conflict, missing prereq, etc.)
- Friendly, intuitive navigation per role

---

### 🔐 Auth System (Owner: Borsato A.)

- [ ] Password hashing on registration using bcrypt
- [ ] Role-based access control using Flask-Login
- [ ] Session management
- [ ] Route guards: unauthorized users redirected cleanly
- [ ] Sysadmin-only user creation enforced server-side

---

### 🧪 Testing & QA (possible EC)

- [ ] Manual test plan document covering all user flows
- [ ] Test cases: prerequisite enforcement (positive + negative)
- [ ] Test cases: schedule conflict detection (overlapping, 30-min gap edge case)
- [ ] Test cases: grade lock (faculty cannot re-submit)
- [ ] Test cases: role authorization (student cannot access GS routes, etc.)
- [ ] Test cases: PhD-only 6000-level restriction
- [ ] Final integration smoke test before submission

---

### 📝 Documentation (Owner: Elsawalhi A.)

- [ ] README: setup instructions, how to seed DB, how to run Flask app
- [ ] ER diagram (finalized, included in submission)
- [ ] Relational schema writeup
- [ ] Brief description of design decisions (scalability notes for Phase 2)
- [ ] Phase 1 report / writeup

---

## Schedule & Milestones

> Dates should be updated if the instructor posts different checkpoints, but the order of work should stay the same.

| Week | Goal | Owner(s) |
|---|---|---|
| Week x | ER diagram draft, agree on schema, repo setup | All |
| Week x | DB schema finalized + SQL scripts; Flask app skeleton | Borsato, Elsawalhi |
| Week x | Auth system + student registration/login working | Borsato, Elsawalhi |
| Week x | Course browser, add/drop with conflict + prereq checks | Elsawalhi, Parekh |
| Week x | Faculty grade entry, GS features, sysadmin | Elsawalhi, Borsato |
| Week x | Transcript view, UI polish, flash messages | Parekh |
| Week x | Full integration testing, bug fixes | All |
| Week x | Documentation, report writeup, final review | Elsawalhi, all review |
| **Submission** | **Everything merged, tested, submitted** | **All** |

---

## Database Design Guidelines

### General Rules
- Use surrogate PKs (`AUTO_INCREMENT INT`) for all tables
- All foreign keys must have explicit constraints defined
- No nullable columns unless there's a real business reason (e.g., `prereq2` is nullable)
- Store passwords as bcrypt hashes
- Use `ENUM` for fixed value sets (e.g., grade, day of week, program type, role)

### Key Design Decisions
- **Users table:** single `users` table with a `role` column (`student`, `faculty`, `gs`, `admin`) — avoids duplication of auth logic
- **Course catalog vs. schedule:** keep these as separate tables. `course_catalog` stores static course info; `schedule` stores the offered sections (links to catalog + adds day/time/instructor/semester). This makes Phase 2 multi-section support trivial.
- **Enrollment table:** links student ↔ schedule section, stores grade (default `IP`)
- **Grades:** stored on the enrollment record. A `grade_locked` boolean flag prevents faculty from changing it after submission.
- **Prereqs:** store as two nullable FK columns on `course_catalog` (`prereq1_id`, `prereq2_id`) pointing back to the same table (self-referential)

### Scalability Notes (for Phase 2)
- `schedule` table should have a `section_number` column even if always `1` in Phase 1
- Add `room` and `capacity` columns to `schedule` now (nullable in Phase 1, activate in Phase 2)
- Keep semester/year on `schedule` rows so different semesters can have different schedules later
- `enrollment` already links to a specific `schedule` row (not just a course), so multiple sections are supported by design

### Valid Values Reference
- **Grades:** `A`, `A-`, `B+`, `B`, `B-`, `C+`, `C`, `F`, `IP`
- **Days:** `M`, `T`, `W`, `R`, `F`
- **Time slots:** `15:00–17:30`, `16:00–18:30`, `18:00–20:30`
- **Programs:** `Masters`, `PhD`
- **Roles:** `student`, `faculty`, `gs`, `admin`

---

## Coding Guidelines

### General

- Every route should have **server-side validation** — never trust the client alone

### Flask Conventions
- Use [**Blueprints**](https://www.geeksforgeeks.org/python/flask-blueprints/) to organize routes by role (`student_bp`, `faculty_bp`, `gs_bp`, `admin_bp`)
- Keep business logic out of route functions — put it in helper/service modules
- Use `flash()` for user-facing messages; categorize as `success`, `error`, `warning`
- Always redirect after a POST (PRG pattern) to prevent double-submit

### Database Access
- Use parameterized queries — **no string interpolation in SQL** (SQL injection prevention)
- Open DB connections per request, close in teardown (or use a connection pool)
- Keep raw SQL in dedicated query functions, not inline in routes

### Security
- Hash passwords with bcrypt
- Enforce role checks server-side with a decorator (e.g., `@require_role('faculty')`)
- Never expose internal DB errors to the user — log them, show a generic message

### File Structure (suggested)
```
regs/
├── app.py               # App factory
├── config.py            # Config (DB creds from env)
├── db.py                # DB connection helpers
├── models/              # Query functions per entity
│   ├── user.py
│   ├── course.py
│   ├── enrollment.py
│   └── grade.py
├── routes/              # Blueprints
│   ├── auth.py
│   ├── student.py
│   ├── faculty.py
│   ├── gs.py
│   └── admin.py
├── templates/           # Jinja2 HTML templates
│   ├── base.html
│   ├── auth/
│   ├── student/
│   ├── faculty/
│   ├── gs/
│   └── admin/
├── static/              # CSS, JS
├── sql/
│   ├── schema.sql
│   └── seed.sql
└── tests/
    └── test_*.py
```

---

## Git Workflow

- `main` branch = stable, submission-ready code only
- `dev` branch = integration branch, merge features here first
- Feature branches: `feature/<name>` (e.g., `feature/add-drop`, `feature/grade-entry`)
- **Never push directly to `main`** — always go through a PR with at least one review
- Commit messages: short, imperative, descriptive (e.g., `Add prereq check to enrollment route`)
- Resolve merge conflicts together — don't just force-push

### PR Checklist (before merging to dev)
- [ ] Feature works end-to-end locally
- [ ] No debug prints or commented-out dead code
- [ ] At least one teammate has reviewed
- [ ] README updated if setup steps changed

---

## Meeting Norms

???

---

## Phase 2 Forward-Thinking Notes

Keep these in mind while building Phase 1 so we don't have to rip things apart later:

- **Multiple sections per course:** `schedule` table design must support it (use `section_number` column from day one)
- **Course catalog management:** an admin UI to add/edit courses will likely be required — keep catalog as its own table
- **Reporting queries:** design the schema so these are easy JOINs, not painful workarounds:
  - All students by degree or admit year → store `program` and `admit_year` on student
  - Full transcript with GPA → store numeric grade equivalent or compute on the fly from grade enum
  - All courses a faculty member teaches → enrollment + schedule + user JOIN
- **Room & capacity:** add columns now, enforce in Phase 2
- **Semester scheduling:** the system assumes same schedule every semester in Phase 1, but the `schedule` table should have `semester` + `year` columns so Phase 2 can vary it
- **GPA calculation:** agree on a grade point scale now so it's consistent when we implement it:
  - A=4.0, A-=3.7, B+=3.3, B=3.0, B-=2.7, C+=2.3, C=2.0, F=0.0, IP=excluded

---

*****An idiot admires complexity, a genius admires simplicity — Terry A. Davis (1969 - 2018)*****