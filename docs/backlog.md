
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

- **`modularity/registry.py` — edge-case tests**
  Type: Task · Priority: Medium · Created: 2026-03-17
  Description: Cover registry edge branches and failure cases.
  Files: `src/abcdef/modularity/registry.py`, tests → `tests/abcdef/modularity/test_registry.py`
  Rationale: Small uncovered branches (≈5 misses).

- **CQRS components — cover message/document flow edge cases**
  Type: Task · Priority: Medium · Created: 2026-03-17
  Description: Add tests for `c/document_store.py` (missing-doc and error flows), `c/message_bus.py` (subscriber errors, no-subscriber case), `c/projector.py` and `c/query.py` edge cases.
  Files: `src/abcdef/c/*.py`, tests → `tests/abcdef/c/`
  Rationale: Close multiple small gaps and guard CQRS behavior.

- **DDD / repository tests**
  Type: Task · Priority: Medium · Created: 2026-03-17
  Description: Add tests for `d/repository.py` and `d/aggregate.py` edge cases (load/save/delete, no-record cases).
  Files: `src/abcdef/d/*.py`, tests → `tests/abcdef/d/`
  Rationale: Improve confidence around repository semantics.

- **DE event-sourcing tests**
  Type: Task · Priority: Medium · Created: 2026-03-17
  Description: Add tests covering `de/aggregate_store.py`, `de/event_sourced_aggregate.py`, `de/event_store.py` for `VersionConflictError`, snapshot behaviour, and append/read semantics.
  Files: `src/abcdef/de/*.py`, tests → `tests/abcdef/de/`
  Rationale: Fill coverage gaps and test optimistic concurrency.

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

