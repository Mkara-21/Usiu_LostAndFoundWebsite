# Member 4 — Backend 2: authentication and access control

## Branch

```text
feature/authentication
```

## Your assignment

You own authentication, sessions, and access control. Review the included routes
and helpers, run both test files, and make a genuine reviewed improvement before
committing. Be ready to explain USIU email validation, six- versus nine-digit
IDs, strong passwords, hashing, duplicate handling, login role matching,
complete logout, guest redirects, and HTTP 403 responses.

## Routes and helpers

```text
GET  /auth
POST /signup
POST /login
GET  /logout
login_required(view)
role_required(*allowed_roles)
is_allowed_image(filename)
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_authentication.py tests/test_access_control.py -q
```

## Suggested commits

```text
feat(auth): implement signup login and logout
feat(auth): enforce USIU credential and password policies
test(auth): cover sessions and role access
```

## Presentation summary

“I implemented secure role-aware authentication. Passwords are hashed, IDs and
emails follow USIU rules, sessions store only required identity fields, logout
clears the session, and decorators prevent unauthorised cross-role access.”
