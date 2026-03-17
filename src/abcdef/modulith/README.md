# Modulith — Modular Architecture Validation and Documentation

Tools for application developers to enforce, validate, and document the modular architecture of their applications built on the ABCDEF framework.

## Purpose

`abcdef.modulith` helps applications declare their module structure explicitly and enforce architectural constraints:

- **Explicit module declaration** — each module declares its type (command or query) and metadata via `__modulith__` dict in `__init__.py`
- **Validation** — checks that modules respect their declared type and don't cross architectural boundaries
- **Documentation** — generates clean Markdown showing each module's public API and inter-module communication (events, SPIs)

## Quick Start

### 1. Declare a Module

In each module's `__init__.py`:

```python
"""Order management and fulfillment."""

# ... your exports ...

__modulith__ = {
    "type": "command_module",  # or "query_module"
    "name": "orders",          # optional: defaults to package name
    "description": "...",      # optional: defaults to docstring above
}
```

### 2. Validate and Generate Docs

```python
from pathlib import Path
from abcdef.modulith import Modulith

modulith = Modulith(Path.cwd())
modules = modulith.discover()
violations = modulith.validate()
docs = modulith.generate_docs()

# Print violations (if any) or save docs
if violations:
    for v in violations:
        print(f"{v.module_name}: {v.message}")
else:
    Path("MODULES.md").write_text(docs)
```

## Module Types

### Command Module

Write side. Maintains aggregates, enforces invariants, publishes events.

**Allowed exports:**
- `@command` — commands that trigger state changes
- `@domain_event` — domain events published by this module
- `@spi` — abstract interfaces exposed to other modules

**Not allowed:**
- `@query` — queries belong on the read side

### Query Module

Read side. Projects events into read models, serves queries.

**Allowed exports:**
- `@query` — queries that read without mutating
- `@document` — denormalised read model types
- `@spi` — abstract interfaces exposed to other modules

**Not allowed:**
- `@command` — commands belong on the write side

## Public API Boundaries

Modules communicate **only through their root exports** (`__init__.py`).

- **Events published** — commands/queries/events declared in root and decorated with framework markers
- **SPIs** — abstract classes marked with `@spi` (modulith marker)
- **No internal imports** — layers (domain, application, infrastructure, projection) must not import from other modules' internals

## Validation Checks

### Read/Write Constraints

Command modules cannot export queries. Query modules cannot export commands.

### Facade Rule

Module `__init__.py` may only re-export symbols from its own namespace. No cross-module re-exports.

### Import Boundaries

Layer files must only import from other modules' root exports, not from their internals.

## Documentation Generation

The `generate_docs()` method produces Markdown describing:

- **Module type** — command or query
- **Description** — from `__init__.py` docstring or explicit metadata
- **Public API** — commands, queries, events, SPIs exported at root
- **Nothing else** — implementation details (layers, domain types, internal structure) are omitted

This focuses documentation on *what a module does* and *how it communicates*, not *how it's implemented*.

## Module Discovery

The `discover()` method scans the project for packages declaring `__modulith__` and loads them as `CommandModule` or `QueryModule` objects. It:

- Recursively walks the project from the root path
- Skips `tests/`, `venv/`, and `abcdef/` directories
- Reads each package's `__init__.py` for the `__modulith__` dict
- Extracts the module's docstring as description if not explicitly set
- Discovers the module's public API by importing and inspecting exported symbols

## Error Handling

- **Missing type** — raises `ValueError` if `__modulith__['type']` is absent
- **Invalid type** — raises `ValueError` if type is not `"command_module"` or `"query_module"`
- **Import errors** — captured gracefully; module structure is still discoverable even if imports fail
- **Violations** — collected and returned as `Violation` objects, not raised as exceptions

## Usage in Tests

Use `modulith.validate()` in a test to enforce boundaries:

```python
def test_module_boundaries():
    """Enforce modulith architecture constraints."""
    modulith = Modulith(Path(__file__).parent.parent.parent)
    modulith.discover()
    violations = modulith.validate()
    
    assert violations == [], "\n".join(
        f"{v.module_name}: {v.message}" for v in violations
    )
```

## Markers

Modulith recognises markers from the framework:

| Marker | Attribute | From | Purpose |
|---|---|---|---|
| `@command` | `__cqrs_type__ = "command"` | `abcdef.c.markers` | Command in CQRS |
| `@query` | `__cqrs_type__ = "query"` | `abcdef.c.markers` | Query in CQRS |
| `@domain_event` | `__ddd_type__ = "domain_event"` | `abcdef.d.markers` | Domain event in DDD |
| `@spi` | `__modulith_type__ = "spi"` | `abcdef.modulith.markers` | Service Provider Interface |

No new decorators are needed for most code; the framework markers are sufficient. `@spi` is the only modulith-specific marker and is optional (use it to explicitly mark abstract base classes intended as contracts).

## Public API

**Entry point:**

- `Modulith(root_path)` — discover and validate modules

**Results:**

- `Module` (ABC), `CommandModule`, `QueryModule` — discovered module objects
- `PublicApi`, `PublicApiSymbol` — extracted API details
- `Violation` — architecture constraint violations

**Validation:**

- `BoundaryValidator.validate()` — check read/write, facade, and import constraints

**Documentation:**

- `MarkdownReporter.generate()` — produce Markdown docs from modules

## Limitations and Future Work

- **Module import resolution** — currently uses heuristics to map Python package paths to logical module names; may not work for complex nested structures
- **Cross-module event subscriptions** — discovery detects which modules import event types, but does not model subscription routing
- **Circular dependencies** — not explicitly detected; will be added if needed
- **Custom validation rules** — not yet supported; extend `BoundaryValidator` for custom checks

