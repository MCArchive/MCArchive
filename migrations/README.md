# DB Migrations

This folder contains database migration scripts for MCArchive. Every time a
schema change is made, a migration script must be written to migrate the
database to and from the new schema.

To upgrade the DB to the latest schema, or create tables in a new DB, run
`flask db upgrade`.

To generate some basic migration scripts after a schema change, run `flask db
migrate` and then review the generated script. Alembic cannot generate perfect
migrations, so some things must be written manually.

