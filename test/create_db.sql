-- ADD `.read schemas/*.sql` for every new schema
-- RUN with `sqlite3 database.db < create_db.sql`

.read schemas/users.sql
.read schemas/catalog.sql
.read schemas/schedule.sql
.read schemas/enrollment.sql
.read schemas/seed_users.sql
.read schemas/seed_catalog.sql
.read schemas/seed_offerings.sql
.read schemas/seed_enrollment.sql
VACUUM;