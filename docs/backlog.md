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

## Bugs

### `_categorise` silently mis-categorises symbols when kind upgrade is skipped

```
Priority: High
Created:  2026-03-18
Files:    src/abcdef/modularity/extraction.py
```

In `PublicApiExtractor._categorise`, after appending an "unknown" placeholder to
`symbols`, the code overwrites `symbols[-1]` with the typed symbol (`command`, `query`,
`event`, `spi`). If that assignment is absent or broken, the symbol remains
`kind="unknown"` in `PublicApi.symbols` while still being added to the typed set
(commands/queries/events/spis). The discrepancy means callers that iterate `api.symbols`
see wrong kinds, and any code that relies on symbol kind for routing or reporting
silently misbehaves.

Rationale: the entire modularity classification system depends on correct symbol kinds;
a silent mis-categorisation is undetectable without explicit assertions.

Suggested tests: add tests asserting that after extraction, symbols present in
`api.commands`, `api.queries`, `api.events`, and `api.spis` also appear in `api.symbols`
with the matching `kind` field (not `"unknown"`).

______________________________________________________________________

## Tasks

### Test that boundary loop guards use `continue`, not `break`

```
Priority: High
Created:  2026-03-18
Files:    src/abcdef/modularity/validation_boundary.py, tests for boundary validation
```

`_validate_import_boundaries` and `_validate_facade_rule` both contain guards that skip
`__init__.py` files and `abcdef`-prefixed imports using `continue`. Replacing either
with `break` stops the scan early, causing all subsequent files/imports to be silently
ignored. No test currently verifies that scanning continues past a skipped entry and
still detects violations in later entries.

Rationale: a `continue`→`break` regression makes the entire boundary scanner ineffective
with no error; it is only detectable by asserting violations are found after a skipped
item.

Suggested tests: write a scenario with a skipped file/import followed by a genuine
violation, and assert the violation is reported.

______________________________________________________________________

### Test that `abcdef`-prefixed imports are excluded from boundary violations

```
Priority: High
Created:  2026-03-18
Files:    src/abcdef/modularity/validation_boundary.py, tests for boundary validation
```

Both `_validate_facade_rule` and `_validate_import_boundaries` skip any `ImportFrom`
node whose module starts with `"abcdef"`. No test currently imports an `abcdef.*` symbol
and asserts it produces no violation. A mutation to the guard string (`"ABCDEF"`,
`"XXabcdefXX"`) survives undetected.

Rationale: framework-internal imports must never trigger false-positive violations;
absence of this test leaves the exclusion guard unverified.

Suggested tests: create a module whose `__init__.py` or layer file imports from
`abcdef.*`; assert zero violations are reported.

______________________________________________________________________

### Test that intra-module layered imports are not flagged as facade violations

```
Priority: High
Created:  2026-03-18
Files:    src/abcdef/modularity/validation_boundary.py, tests for facade validation
```

`_validate_facade_rule` allows imports whose module equals `module_prefix` or starts
with `module_prefix + "."`. The sub-module check (`startswith(module_prefix + ".")`) is
untested; a mutation replacing `"."` with `"XX.XX"` survives, meaning every layered
intra-module import (`orders.domain`, `orders.application`, etc.) would be falsely
flagged.

Rationale: without this test, the sub-namespace allowance is effectively dead code from
a coverage perspective.

Suggested tests: create a module `__init__.py` that imports from its own sub-namespace
(e.g. `from orders.domain import Foo`); assert no facade violation.

______________________________________________________________________

### Assert `violation.message` and `violation.location` content in boundary tests

```
Priority: Medium
Created:  2026-03-18
Files:    src/abcdef/modularity/validation_boundary.py, tests for all three validators
```

Tests for `_validate_read_write_constraints`, `_validate_facade_rule`, and
`_validate_import_boundaries` appear to assert only that violations are returned (count
or presence), not what those violations contain. Mutations that set `message=None` or
`location=None` (or a wrong path) all survive. This leaves the diagnostic quality of
violation output untested.

Rationale: violations with `None` message or wrong location silently degrade the
developer experience; the only way to catch this is explicit field assertions.

Suggested tests: for each validator, assert `violation.message` contains the expected
substring and `violation.location` matches the expected file path.

______________________________________________________________________

### Assert rendered file content and encoding in codegen generator tests

```
Priority: Medium
Created:  2026-03-18
Files:    src/abcdef/codegen/generator.py, codegen generator tests
```

Tests for `generate_module` and `generate_feature` do not assert the content of
generated files in enough detail. Template variable key mutations (`"module_type"` →
`"XXmodule_typeXX"`, `"aggregate_pascal"` → `"XXaggregate_pascalXX"`, etc.) all survive,
meaning un-substituted placeholders would appear in output undetected. Additionally,
`_write` accepts `encoding=None` (platform default) without test failure, risking silent
encoding regressions on non-UTF-8 systems.

Rationale: broken template substitution produces syntactically valid but semantically
wrong scaffold files — a silent failure that would only surface at runtime in the
generated application.

Suggested tests: assert generated file text contains expected substitutions for each
template variable (module name, pascal name, aggregate name, etc.). Assert `_write`
passes `encoding="utf-8"` by checking the written file can be read back as UTF-8 with
the expected content.

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

Approximately 60 of the 113 stable survivors (mutation run 2026-03-18) are pure noise:
string-literal mutations on CLI help text, error message casing, `prog=` /
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
count drops by ~60 with no previously-killed mutants now surviving.
