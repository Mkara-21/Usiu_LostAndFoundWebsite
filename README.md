# USIU-A Lost & Found Website

A Flask and SQLite application for securely reporting, tracking, and reclaiming
items lost on the USIU-A campus. Students can report recovered belongings,
search available records, and submit private ownership claims. Security officers
verify items, check them into storage, review evidence, and confirm returns.

## Features

- USIU-A student and security account registration and login
- Official email, role-specific ID, and strong-password validation
- Hashed passwords and role-protected routes
- Safe finder reports with optional image uploads
- Public item details with private identifiers protected from students
- Available-item search and category filtering
- Ownership claims linked to specific items
- Security check-in, approval, denial, and return workflows
- Enforced item and claim status transitions
- Responsive student and security dashboards
- Accessible labels, focus states, alternative text, and reduced-motion support
- Demonstration accounts and data
- Automated backend, frontend-contract, accessibility, and integration tests

## Technology

- Python 3
- Flask 3.1
- SQLite
- Jinja templates
- Plain CSS and JavaScript
- pytest

## Project structure

```text
auth_routes.py                  Authentication and sessions
claim_routes.py                 Item listing and ownership claims
student_routes.py               Student dashboard and finder reports
security_routes.py              Security verification workflow
route_helpers.py                Shared access and upload helpers
usiulostnfound_app.py           Flask application factory
usiulostnfound_database.py      SQLite schema and connection helper
seed_mockdata.py                Demonstration accounts and records
templates/                      Modular Jinja interfaces
static/                         CSS, JavaScript, and runtime uploads
tests/                          Unit, template, and integration tests
```

## Local setup

From PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set a private session key when running outside local development:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-value"
```

## Load demonstration data

```powershell
.\.venv\Scripts\python.exe seed_mockdata.py
```

The command safely creates the schema, keeps existing accounts, and refreshes
the demonstration items and claims.

### Demonstration accounts

| Role | ID | Password |
|---|---:|---|
| Security | `123456789` | `Security@123` |
| Student | `100200` | `Student@123` |
| Student | `205311` | `Student@123` |

These credentials are for local demonstration only.

## Run the application

```powershell
.\.venv\Scripts\python.exe usiulostnfound_app.py
```

Open <http://127.0.0.1:5000/>.

## Run verification

```powershell
.\.venv\Scripts\python.exe -m py_compile usiulostnfound_app.py usiulostnfound_database.py route_helpers.py auth_routes.py student_routes.py claim_routes.py security_routes.py seed_mockdata.py
.\.venv\Scripts\python.exe -m pytest -q
node --check static\usiulostnfound.js
```

## Status workflow

```text
Item:  Pending Security -> Checked-In -> Claimed
Claim: Pending -> Approved or Denied
```

An approved claim requires the linked item to be checked into security storage.
Approval updates both the claim and the item in the same transaction.

## Local data and uploads

The SQLite database and uploaded images are generated at runtime and ignored by
Git. Uploads are limited to 5 MB and restricted to PNG, JPG, JPEG, WEBP, and GIF
filenames. Never commit database files, virtual environments, uploaded user
content, caches, secrets, or local screenshot artifacts.
