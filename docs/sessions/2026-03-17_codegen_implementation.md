# Codegen Implementation Session

**Date:** 2026-03-17\
**Objective:** Implement `abcdef.codegen` — a scaffolding tool that generates
boilerplate module and feature directory trees for applications built on the framework.

______________________________________________________________________

## Decisions Made

### 1. `string.Template` (stdlib) over Jinja2

**Decision:** Use Python's stdlib `string.Template` for all template rendering. No
third-party dependency added.

**Rationale:** The skeletons are simple enough that `$variable` substitution covers all
cases. Jinja2 would add a dev dependency and complexity for no current benefit.

**Alternatives considered:** Jinja2 for conditional logic and loops — deferred. If
templates need branching, migrate then.

**Impact:** Zero new runtime or dev dependencies. Templates are `.tmpl` files with
`$variable` placeholders.

______________________________________________________________________

### 2. Templates emit string literals, not imported constants

**Decision:** `__init__.py` templates emit `"$module_type"` (resolving to
`"command_module"` or `"query_module"`) rather than
`from abcdef.modularity.markers import COMMAND_MODULE` + the symbol name.

**Rationale:** `abcdef.modularity`'s AST extractor (`_extract_modularity_dict`) only
captures dict values that are `ast.Constant` string literals. Emitting a name reference
(`COMMAND_MODULE`) causes the extractor to miss the `type` key entirely, making
generated modules undiscoverable and `generate_feature` unable to infer the module type.

**Alternatives considered:** Patching the extractor to also resolve name references —
rejected as overreach; the extractor's conservatism is intentional.

**Impact:** Generated `__init__.py` files are standalone and do not import the marker
constant. The string value is the contract, not the symbol.

______________________________________________________________________

### 3. `generate_feature` infers module type via AST, does not accept a flag

**Decision:** `generate_feature` reads the existing `__init__.py` `__modularity__` dict
via AST parse to determine whether to emit command or query templates. No `--type` flag
on the CLI.

**Rationale:** The module type is already declared in `__init__.py`. Requiring the user
to repeat it is redundant and creates a consistency risk.

**Impact:** `generate_feature` fails with a clear `ValueError` if `__init__.py` is
missing or has no valid `__modularity__` declaration.

______________________________________________________________________

### 4. `generate_feature` does not touch `__init__.py`

**Decision:** Export wiring (adding symbols to `__all__`) is left entirely to the
developer.

**Rationale:** The framework cannot know which symbols from a new feature should be
exported — that is a domain and API contract decision. Agreed in the original design
conversation.

**Impact:** Developer must manually update `__init__.py` after running `feature`.

______________________________________________________________________

### 5. Placeholder file names for module-level stubs

**Decision:** The initial stubs created by `module` use the filename `placeholder.py`
for application, infrastructure, and CLI layers. The domain aggregate and projection
files are named after the module (`orders.py`, `orders_repository.py`, `reports.py`).

**Rationale:** Domain files have a natural name derived from the module. Application,
infrastructure, and CLI stubs are intentionally temporary — `placeholder.py` signals
that they should be replaced by real feature files via `feature` or by hand.

**Impact:** `feature` creates new files alongside `placeholder.py`; it does not replace
it. The developer removes `placeholder.py` when it is no longer needed.

______________________________________________________________________

## Assumptions

### 1. `Modularity._extract_modularity_dict` is stable enough to call directly

**Assumption:** Calling `Modularity._extract_modularity_dict(tree)` from `generator.py`
(with `# noqa: SLF001`) is acceptable given the pre-production stance and that
`generator.py` lives in the same codebase.

**Risk:** If the method is refactored or renamed, `generator.py` breaks silently.

**Verification plan:** The integration tests exercise this path on every CI run. A
rename would surface immediately.

**Status:** Acceptable. If this becomes a maintenance burden, extract a shared
`_parse_modularity_dict` utility into `modularity/` with a public or semi-public
surface.

______________________________________________________________________

### 2. Placeholder stubs in generated files will not be imported at runtime

**Assumption:** The placeholder infrastructure and application files contain
`raise NotImplementedError` stubs. No test or runtime code will attempt to instantiate
them before the developer replaces them.

**Status:** Acceptable. These are development scaffolds, not production artifacts.

______________________________________________________________________

## Blockers & Uncertainties

### 1. Template variable greedy matching

**Blocker:** `string.Template.substitute` matched `$document_pascal_store` and
`$aggregate_pascal_repository` as unknown variables in infrastructure template comments,
raising `KeyError`.

**Status:** Resolved — braced all multi-word references in comments:
`${document_pascal}Store`, `${aggregate_pascal_repository}`.

______________________________________________________________________

### 2. AST extractor cannot read name-reference dict values

**Blocker:** Generated `__init__.py` used `COMMAND_MODULE` symbol (not a string literal)
as the `type` value. The AST extractor returned `None` for `type`, causing both
`Modularity.discover()` and `_read_module_type()` to raise `ValueError`.

**Status:** Resolved — templates now emit `"$module_type"` which renders to a string
literal.

______________________________________________________________________

## Artefacts

### Code

**New package:** `src/abcdef/codegen/`

- `__init__.py` — public API: `generate_module`, `generate_feature`
- `generator.py` — core rendering logic; `_to_pascal`, `_render`, `_write`,
  `_read_module_type`, `generate_module`, `generate_feature`
- `cli.py` — `argparse`-based `main()`; subcommands `module` and `feature`
- `README.md` — package documentation with CLI usage and Python API examples

**Templates:** `src/abcdef/codegen/templates/`

- `command_module/__init__.py.tmpl`
- `command_module/domain/aggregate.py.tmpl`
- `command_module/domain/aggregate_repository.py.tmpl`
- `command_module/application/use_case.py.tmpl`
- `command_module/infrastructure/placeholder.py.tmpl`
- `command_module/interface/cli/use_case.py.tmpl`
- `query_module/__init__.py.tmpl`
- `query_module/projection/document.py.tmpl`
- `query_module/application/query.py.tmpl`
- `query_module/infrastructure/placeholder.py.tmpl`
- `query_module/interface/cli/query.py.tmpl`

**Tests:** `tests/abcdef/codegen/`

- `__init__.py`
- `test_generator.py` — 24 unit tests: `_to_pascal`, `generate_module`,
  `generate_feature`
- `test_cli.py` — 15 tests: both sub-commands via `main()`, exit codes, stdout/stderr,
  argparse error paths
- `test_integration.py` — 7 anti-drift tests: generated modules validated with
  `Modularity(...).validate()`

**Test summary:** 70 new tests, all passing. Total suite: 408 tests.

### Modified files

- `pyproject.toml` — added `[project.scripts]` with `abcdef-gen` entry point
- `src/abcdef/__init__.py` — added `abcdef.codegen` to package map docstring
- `src/abcdef/README.md` — added `codegen/` to structure tree and per-brick guides
- `README.md` — added `abcdef.codegen` to core packages list and per-brick guides

### Commits

- **SHA:** _(fill in after `git commit`)_\
  `feat: add abcdef.codegen package with abcdef-gen CLI scaffolding tool`

______________________________________________________________________

## AI Interaction Summary

**Clarification rounds:** 0 (design carried forward from prior session transcript)

**Major pivots:** 0

**Interventions needed:** 2 bug fixes after first CI run:

1. `KeyError: 'document_pascal_store'` — template comment used unbraced `$variable` that
   resolved to an unknown key. Fixed by bracing: `${document_pascal}Store`.
1. `__modularity__['type'] is 'None'` — templates emitted the imported symbol name
   rather than a string literal; the AST extractor requires string literals. Fixed by
   emitting `"$module_type"` instead.

**Quality of outputs:** Code correct after two targeted fixes. Tests comprehensive and
well-structured. Integration test (anti-drift) caught both bugs immediately.

______________________________________________________________________

## Lessons Learned

- **`string.Template` greediness in comments:** Any `$word` in a template is a
  substitution target, including in comments. Brace all multi-segment references
  explicitly (`${var}`) or avoid `$` in non-substitution text.
- **AST extractor conservatism is a feature:** The extractor only reads string
  constants, by design. Templates that emit name references rather than literals break
  discovery silently. Integration tests are the only reliable guard.
- **Anti-drift tests earn their keep:** Both bugs were caught by tests, not by manual
  inspection. The test suite is the specification.

______________________________________________________________________

## Next Steps (Not in Scope)

- [ ] Add `codegen` validation to `test_boundaries.py` facade checks if it grows a
  public API surface beyond `generate_module` / `generate_feature`
- [ ] Consider extracting `_parse_modularity_dict` as a semi-public utility in
  `modularity/` if more packages need to read `__modularity__` dicts
- [ ] Replace `placeholder.py` stubs with more descriptive names if user feedback
  suggests confusion
