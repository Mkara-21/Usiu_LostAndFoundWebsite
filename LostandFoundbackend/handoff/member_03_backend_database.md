# Member 3 — Backend 1: database and demonstration data

## Branch

```text
feature/database-and-seeding
```

## Your assignment

You own the database and demonstration-data package. Place the included files in
the project, read the schema and seed logic, run the database tests, and make at
least one reviewed improvement or documentation correction before committing.
You must understand connection cleanup, row access, foreign keys, idempotent
table/account creation, password hashing, indexes, status checks, and repeatable
demo seeding.

## Key functions

- `get_connection(database_path=None)` opens SQLite with `sqlite3.Row` and FKs.
- `init_db(database_path=None)` creates tables/indexes and one security account.
- `seed(database_path=None)` refreshes items/claims and tops up demo students.

## Tests

```powershell
.\.venv\Scripts\python.exe usiulostnfound_database.py
.\.venv\Scripts\python.exe seed_mockdata.py
.\.venv\Scripts\python.exe -m pytest tests/test_database.py -q
```

## Suggested commits

```text
feat(db): add SQLite schema and connection management
feat(seed): add repeatable demonstration records
test(db): verify schema constraints and seed data
```

## Presentation summary

“I implemented an idempotent SQLite layer with named rows, foreign-key
enforcement, lifecycle constraints, indexes, hashed demo accounts, and repeatable
seed data. My tests verify schema creation, uniqueness, and status coverage.”
