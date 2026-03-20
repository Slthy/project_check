-- ADD `.read schemas/*.sql` for every new schema
-- RUN with `sqlite3 database.db < create_db.sql`

.read schemas/catalog.sql
.read schemas/users.sql

VACUUM;