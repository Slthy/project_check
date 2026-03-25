-- ADD `.read schemas/*.sql` for every new schema
-- Run with: sqlite3 -bail database.db < create_db.sql

.print '--- Creating Schemas ---'
.read schemas/users.sql
.read schemas/catalog.sql
.read schemas/schedule.sql
.read schemas/enrollment.sql

.print '--- Seeding Data ---'

.print '1'
.read schemas/seed_users.sql

.print '2'
.read schemas/seed_catalog.sql

.print '3'
.read schemas/seed_offerings.sql

.print '4'
.read schemas/seed_enrollment.sql

COMMIT;
VACUUM;
