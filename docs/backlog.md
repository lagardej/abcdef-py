# Backlog

Short-listed items: bugs, improvements, and refactoring tasks. Resolved entries are
removed.

______________________________________________________________________

## Conventions

- **One commit per item.** Each backlog item is addressed in its own commit.
- **Remove on resolve.** Completed items are deleted from this file, not marked Done.
  The git log is the record of what was done and when.
- **Types:** `Bug` — incorrect behaviour; `Task` — missing or incomplete work (e.g.
  tests, implementation); `Improvement` — quality, tooling, or documentation.
- **Priorities:** `High` — blocks progress or correctness; `Medium` — should be done
  soon; `Low` — nice to have, no urgency.
- **Agents:** follow the one-commit-per-item rule. Do not batch unrelated items into a
  single commit. Do not add speculative items to this backlog.

______________________________________________________________________

## Backlog item template

Use this template to add or triage backlog items. Keep entries concise and include the
priority.

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

______________________________________________________________________

## Bugs

(none)

______________________________________________________________________

## Tasks

(none)

______________________________________________________________________

## Improvements

- Title: Fix broken Markdown tables in docs
- Type: Improvement
- Priority: Low
- Created: 2026-03-17
- Description: mdformat collapses Markdown tables to fit the 88-character wrap limit,
  breaking their rendering. Affected files include README.md, src/abcdef/README.md, and
  any other docs with tables. Replace tables with lists or find an mdformat-compatible
  table format.
- Files: README.md, src/abcdef/README.md, and any other docs containing tables
- Rationale: Docs are part of the codebase and should render correctly.
- Status: Open
