# Member 8 — Frontend 2: student experience

## Branch

```text
feature/student-interface
```

## Your assignment

You own the student interface. Review the dashboard, finder form, item register,
claim form, and JavaScript interactions. Run the template tests, test the page
at desktop and mobile sizes, and make one genuine usability improvement before
committing. Be ready to explain form-field contracts, private-proof messaging,
category/search filtering, empty states, claim item selection, image alternative
text, section visibility, and mobile behavior.

## JavaScript functions to explain

```text
showSection
hideSection
startClaim
filterCategory
filterItems
```

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_student_templates.py -q
node --check static\usiulostnfound.js
```

## Suggested commits

```text
feat(student-ui): build finder and recovery dashboard
feat(student-ui): build ownership claim experience
feat(student-js): connect filtering selection and panels
test(student-ui): verify forms items and empty states
```

## Presentation summary

“I built the student experience for both finder and owner journeys. The
interface protects secret evidence, supports search and categories, connects a
selected item to its claim form, handles empty results, and responds across
screen sizes.”
