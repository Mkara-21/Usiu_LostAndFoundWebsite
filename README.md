# USIU-A Lost & Found Website

A Flask and SQLite application for reporting, tracking, and reclaiming items
lost on the USIU-A campus. Students can act as finders or owners, while security
officers verify recovered items and review ownership claims.

## Technology

- Python 3
- Flask 3.1
- SQLite
- Jinja templates with plain CSS and JavaScript
- pytest

## Project structure

```text
static/                     Styles, JavaScript, and runtime uploads
templates/                  Shared and role-specific Jinja templates
tests/                      Automated tests
usiulostnfound_app.py       Application factory and entry point
usiulostnfound_database.py  SQLite connection and schema setup
route_helpers.py            Shared authorization and upload helpers
*_routes.py                 Contributor-owned Flask blueprints
```

## Local setup

From PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe usiulostnfound_app.py
```

Open <http://127.0.0.1:5000/>. The local SQLite database is created on first
startup and is ignored by Git.

## Configuration

Set `SECRET_KEY` in the environment outside local development. A development
fallback is provided only so the project starts without extra configuration.
Uploads are limited to 5 MB and stored in `static/uploads/`; runtime uploads are
ignored while `.gitkeep` preserves the directory.

## Baseline verification

```powershell
.\.venv\Scripts\python.exe -m py_compile usiulostnfound_app.py usiulostnfound_database.py route_helpers.py auth_routes.py student_routes.py claim_routes.py security_routes.py
.\.venv\Scripts\python.exe -m pytest
```

## Contribution workflow

Before opening a pull request, inspect `git diff`, run the relevant tests, and
confirm that the application starts. Do not commit database files, virtual
environments, uploaded images, caches, or secrets.

No direct commits should be made to `main`, and unmerged branches must be
preserved until their useful work has been reviewed and transferred.
