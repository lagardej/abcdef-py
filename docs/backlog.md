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

## Tasks

### Increase test coverage for user-facing validation errors

```
Priority:  High
Created:  2026-03-21
Files:    src/abcdef/modularity/modularity.py
```

Add tests that verify error messages when `__modularity__` declarations are
misconfigured:

- Missing required `type` field
- Invalid `type` value (not 'command' or 'query')
- Unknown module type in `_create_module()`

Rationale: These paths generate user-facing error messages but lack test verification.
Incorrect or unclear errors would significantly impact developer experience when fixing
module configuration issues.

### Increase test coverage for exception handling in discovery

```
Priority:  Medium-High
Created:  2026-03-21
Files:    src/abcdef/modularity/modularity.py
```

Add tests for the exception handling paths in `Modularity.discover()`:

- Declaration file parsing failures (line 65)
- API extraction failures resulting in empty API fallback (lines 80-82)

Rationale: These defensive paths ensure the system degrades gracefully when encountering
malformed modules. Without tests, regressions could cause crashes or silent data loss
during discovery.

### Increase test coverage for boundary validation exception handling

```
Priority:  Medium-High
Created:  2026-03-21
Files:    src/abcdef/modularity/validation_boundary.py
```

Add tests for exception handling in boundary validation:

- File read/parse failures in `_check_facade_rule()` (lines 49-50)
- File read/parse failures in `_check_import_boundary()` (lines 82-83)

Rationale: These paths handle corrupted or unreadable Python files. The system should
continue validating other modules rather than crashing, but this behavior is untested.

### Increase branch coverage in modularity dict extraction

```
Priority:  Medium
Created:  2026-03-21
Files:    src/abcdef/modularity/modularity.py
```

Add tests to cover the specific branch in `_extract_modularity_dict()` where the dict
comprehension condition evaluates differently (line 165→162).

Rationale: The extraction logic parses complex AST patterns. Uncovered branches indicate
untested AST structures that could cause bugs in edge cases.

### Increase branch coverage in import boundary checking

```
Priority:  Medium
Created:  2026-03-21
Files:    src/abcdef/modularity/validation_boundary.py
```

Add tests to cover the branch from the inner `for prefix in forbidden:` loop back to the
outer `for node in ast.walk(tree):` loop (line 95→85).

Rationale: This nested loop structure validates import boundaries across modules.
Incomplete branch coverage means some combinations of imports and module relationships
are untested.

### Add tests for self-internal import filtering

```
Priority:  Medium
Created:  2026-03-21
Files:    src/abcdef/modularity/validation_boundary.py
```

Add tests that verify the correct handling of self-internal imports (line 93) — imports
from one's own `.internal` package should be allowed.

Rationale: This allows modules to import from their own internal subpackages, a key
design pattern. The filtering logic must be correct to avoid false positives.

### Add test coverage for MarkdownReporter generation

```
Priority:  Medium-Low
Created:  2026-03-21
Files:    src/abcdef/modularity/modularity.py
```

Add tests for `Modularity.generate_markdown()` that exercise the `MarkdownReporter`
instantiation and `generate()` call (lines 109-110).

Rationale: The markdown generation feature is part of the public API but lacks direct
test coverage. While lower priority, regressions could break documentation output.

### Add test for PublicApi.empty() factory method

```
Priority:  Low
Created:  2026-03-21
Files:    src/abcdef/modularity/validation.py
```

Add direct test for `PublicApi.empty()` return statement (line 64) to verify it produces
an API with all empty frozensets.

Rationale: This utility method is likely used in error paths. Current indirect tests may
not verify its correctness explicitly.

### Increase coverage for module validation exceptions

```
Priority:  Low
Created:  2026-03-21
Files:    src/abcdef/modularity/module.py
```

Add tests that intentionally create `CommandModule` and `QueryModule` with invalid
`module_type` to trigger the `__post_init__` validation exceptions (lines 88, 128).

Rationale: These validate internal consistency checks. Low priority because they should
only fire on deliberately invalid usage, but testing ensures error messages remain
accurate.
