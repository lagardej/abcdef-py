
# Backlog

Short-listed items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Backlog item template

Use this template to add or triage backlog items. Keep entries concise and include the priority.

```
- Title: Short descriptive title
- Type: Bug / Task / Improvement
- Priority: High / Medium / Low
- Created: YYYY-MM-DD
- Description: One-paragraph description of the work
- Files: affected files or new files to create
- Rationale: Why this matters (1–2 sentences)
- Suggested tests / steps: (optional)
- Status: Open / In progress / Done
- Notes: (optional)
```

---

## Bugs

(none)

---

## Tasks

(none)

---

## Improvements

- **Add `CONTRIBUTING.md` with test and coverage instructions**
  Type: Improvement · Priority: Low · Created: 2026-03-17
  Description: Short guide showing how to run tests on Windows and Unix (e.g., `python -m pytest -q`, coverage commands), and note `make` is optional on Windows.
  Files: new `CONTRIBUTING.md` at repo root.
  Rationale: Make it easier for contributors to run tests locally.

- **Backlog / roadmap tagging guidance**
  Type: Improvement · Priority: Low · Created: 2026-03-17
  Description: Add a short section in this file describing tags/priority conventions for backlog entries and the “one-commit-per-item” rule.
  Files: `docs/backlog.md` (this file)
  Rationale: Keep backlog disciplined and consistent for agents and contributors.

- **Coverage target issues**
  Type: Improvement · Priority: Low · Created: 2026-03-17
  Description: Add backlog items to track target coverage for `modularity/` (e.g., aim 90%+) and other modules with low coverage.
  Files: `docs/backlog.md`
  Rationale: Track measurable goals for test coverage.

