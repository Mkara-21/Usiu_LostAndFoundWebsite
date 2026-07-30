# Member 6 — Backend 4: security and integration

## Branch

```text
feature/security-and-integration
```

## Your assignment

You own the security workflow and backend integration. Review the routes and app
factory, run the security and integration tests, and make one genuine
improvement before committing. Understand valid status transitions, 404/400/409
failures, approval transactions, why items must be checked in before approval,
repeated-decision rejection, role protection, blueprint registration, upload
limits, and the full finder-to-owner journey.

## Routes

```text
GET  /security
POST /security/items/<item_id>/checkin
POST /security/claims/<claim_id>/decision
POST /security/items/<item_id>/return
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_security_workflow.py tests/test_integration.py -q
```

## Suggested commits

```text
feat(security): add item check-in and dashboard queries
feat(security): add claim decisions and return confirmation
test(integration): verify complete lifecycle and authorization
```

## Presentation summary

“I implemented controlled security transitions. Only pending items can be
checked in, only pending claims can be decided, approval atomically updates the
claim and item, and invalid or repeated actions return precise HTTP errors.”
