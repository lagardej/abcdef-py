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

### Title of the item

```
Priority:  High / Medium / Low
Created:   YYYY-MM-DD
Files:     affected files or new files to create
```

Description: one-paragraph description of the work.

Rationale: why this matters (1–2 sentences).

Suggested tests / steps: (optional)

Notes: (optional)

______________________________________________________________________

## Improvements

### Silence noise mutants with `# pragma: no mutate`

```
Priority: Low
Created:  2026-03-18
Files:    src/abcdef/codegen/cli.py, src/abcdef/codegen/generator.py,
          src/abcdef/modularity/validation_boundary.py,
          src/abcdef/de/event_sourced_repository.py
```

Approximately 80 of the remaining stable survivors (mutation run 2026-03-18-165915) are
pure noise: string-literal mutations on CLI help text, error message casing, `prog=` /
`description=` values, `NotImplementedError` messages, and similar UI strings with no
behavioural significance. mutmut 3 supports `# pragma: no mutate` inline comments to
exclude individual lines from mutation. Add the pragma to all affected lines. The bulk
is in `codegen/cli.py` `_build_parser` (all help/prog/description/metavar strings) and
`main` (print-format strings); smaller clusters in `codegen/generator.py` (error message
strings, placeholder literal values), `modularity/validation_boundary.py` (violation
message string content), and `de/event_sourced_repository.py` (`NotImplementedError`
message).

Rationale: noise survivors require manual triage on every mutation run; silencing them
makes the surviving mutants list actionable at a glance without any loss of meaningful
signal.

Suggested steps: after adding pragmas, re-run `make mutate` and confirm the survivor
count drops significantly with no previously-killed mutants now surviving.
