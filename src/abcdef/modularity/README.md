# Modularity — Modular Architecture Validation and Documentation

Tools for application developers to enforce, validate, and document the modular
architecture of their applications built on the ABCDEF framework.

## Purpose

`abcdef.modularity` helps applications declare their module structure explicitly and
enforce architectural constraints:

- **Explicit module declaration** — each module declares its type (command or query) and
  metadata via `__modularity__` dict in `__init__.py`
- **Validation** — checks that modules respect their declared type and don't cross
  architectural boundaries
- **Documentation** — generates clean Markdown showing each module's public API and
  inter-module communication (events, SPIs)

## Quick Start

### 1. Declare a Module

In each module's `__init__.py`:

```python
"""Order management and fulfillment."""

# ... your exports ...

__modularity__ = {
    "type": "command",         # or "query"
    "name": "orders",          # optional: defaults to package name
    "description": "...",      # optional: defaults to docstring above
}
```

### 2. Validate and Generate Docs

```python
from pathlib import Path
from abcdef.modularity import Modularity

modularity = Modularity(Path.cwd())
modules = modularity.discover()
violations = modularity.validate()
docs = modularity.generate_docs()

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

- **Events published** — commands/queries/events declared in root and decorated with
  framework markers
- **SPIs** — abstract classes marked with `@spi` (modularity marker)
- **No internal imports** — layers (domain, application, infrastructure, projection)
  must not import from other modules' internals

## Validation Checks

### Read/Write Constraints

Command modules cannot export queries. Query modules cannot export commands.

### Facade Rule

Module `__init__.py` may only re-export symbols from its own namespace. No cross-module
re-exports.

### Import Boundaries

Layer files must only import from other modules' root exports, not from their internals.

## Documentation Generation

The `generate_docs()` method produces Markdown describing:

- **Module type** — command or query
- **Description** — from `__init__.py` docstring or explicit metadata
- **Public API** — commands, queries, events, SPIs exported at root
- **Nothing else** — implementation details (layers, domain types, internal structure)
  are omitted

This focuses documentation on *what a module does* and *how it communicates*, not *how
it's implemented*.

## Example: Generated Documentation

### Module Declarations

Two example modules in an application:

**`myapp/orders/__init__.py`** (command module):

```python
"""Order management — create, modify, and fulfill orders."""

from .commands import CreateOrder, FulfillOrder
from .events import OrderCreated, OrderFulfilled

__modularity__ = {
    "type": "command",
    "name": "orders",
}

__all__ = ["CreateOrder", "FulfillOrder", "OrderCreated", "OrderFulfilled"]
```

**`myapp/reports/__init__.py`** (query module):

```python
"""Order reports and analytics — read-only views of order data."""

from .queries import OrderSummary, OrderHistory
from .projections import OrderDocument

__modularity__ = {
    "type": "query",
    "name": "reports",
}

__all__ = ["OrderSummary", "OrderHistory", "OrderDocument"]
```

### Generated Documentation

Running `modularity.generate_docs()` produces:

```markdown
# Module Documentation

This document describes the public API and inter-module communication
for all modules in the application. Implementation details are omitted.

## Modules

- [orders](#orders)
- [reports](#reports)

### orders

**Type:** Command Module

Order management — create, modify, and fulfill orders.

#### Public API

**Commands:**

- `CreateOrder` — myapp.orders.commands.CreateOrder
- `FulfillOrder` — myapp.orders.commands.FulfillOrder

**Events Published:**

- `OrderCreated` — myapp.orders.events.OrderCreated
- `OrderFulfilled` — myapp.orders.events.OrderFulfilled

### reports

**Type:** Query Module

Order reports and analytics — read-only views of order data.

#### Public API

**Queries:**

- `OrderSummary` — myapp.reports.queries.OrderSummary
- `OrderHistory` — myapp.reports.queries.OrderHistory
```

### What's NOT Shown

The generated documentation **intentionally omits**:

- Aggregate classes (`Order`, `OrderItem`)
- Value objects (`OrderId`, `Money`)
- Repositories and stores
- Domain logic and invariants
- Layer structure (domain, application, infrastructure)
- Internal implementation types

This keeps the documentation focused on the public contract: what commands trigger
actions, what queries retrieve data, what events flow between modules.

## Module Discovery

The `discover()` method scans the project for packages declaring `__modularity__` and
loads them as `CommandModule` or `QueryModule` objects. It:

- Recursively walks the project from the root path
- Skips `tests/`, `venv/`, and `abcdef/` directories
- Reads each package's `__init__.py` for the `__modularity__` dict
- Extracts the module's docstring as description if not explicitly set
- Discovers the module's public API by importing and inspecting exported symbols

## Error Handling

- **Missing type** — raises `ValueError` if `__modularity__['type']` is absent
- **Invalid type** — raises `ValueError` if type is not `"command"` or `"query"`
- **Import errors** — captured gracefully; module structure is still discoverable even
  if imports fail
- **Violations** — collected and returned as `Violation` objects, not raised as
  exceptions

## Usage in Tests

Use `modularity.validate()` in a test to enforce boundaries:

```python
def test_module_boundaries():
    """Enforce modularity architecture constraints."""
    modularity = Modularity(Path(__file__).parent.parent.parent)
    modularity.discover()
    violations = modularity.validate()
    
    assert violations == [], "\n".join(
        f"{v.module_name}: {v.message}" for v in violations
    )
```

## Markers

Modularity recognises markers from the framework:

| Marker          | Attribute                       | From                        | Purpose                    |
| --------------- | ------------------------------- | --------------------------- | -------------------------- |
| `@command`      | `__cqrs_type__ = "command"`     | `abcdef.c.markers`          | Command in CQRS            |
| `@query`        | `__cqrs_type__ = "query"`       | `abcdef.c.markers`          | Query in CQRS              |
| `@domain_event` | `__ddd_type__ = "domain_event"` | `abcdef.d.markers`          | Domain event in DDD        |
| `@spi`          | `__modularity_type__ = "spi"`   | `abcdef.modularity.markers` | Service Provider Interface |
|                 |                                 |                             |                            |

No new decorators are needed for most code; the framework markers are sufficient. `@spi`
is the only modularity-specific marker and is optional (use it to explicitly mark
abstract base classes intended as contracts).

## Acknowledgments

`abcdef.modularity` is directly inspired by
[Spring Modulith](https://spring.io/projects/spring-modulith), a library for building
modular Spring applications.

Spring Modulith defined most of the concepts and validation rules implemented here:

- **Module as a first-class design unit** with explicit boundaries and public APIs
- **Read/write separation** via command and query modules (inspired by Spring Modulith's
  command/event publishing distinction)
- **Facade rule** — modules expose only their root; no re-exports of foreign symbols
- **Import boundary validation** — layers within a module must not bypass public APIs to
  import from other modules' internals
- **Documentation focus** on "what" (public API and communication) rather than "how"
  (implementation details)

The key difference: `abcdef.modularity` is tailored for ABCDEF applications (DDD, CQRS,
Event Sourcing) and uses Python idioms (`__modularity__` dict, AST parsing) rather than
Java/Spring conventions. The architecture principles, however, are directly drawn from
Spring Modulith's proven approach.

## Public API

**Entry point:**

- `Modularity(root_path)` — discover and validate modules

**Results:**

- `Module` (ABC), `CommandModule`, `QueryModule` — discovered module objects
- `PublicApi`, `PublicApiSymbol` — extracted API details
- `Violation` — architecture constraint violations

**Validation:**

- `BoundaryValidator.validate()` — check read/write, facade, and import constraints

**Documentation:**

- `MarkdownReporter.generate()` — produce Markdown docs from modules

## Limitations and Future Work

- **Module import resolution** — currently uses heuristics to map Python package paths
  to logical module names; may not work for complex nested structures
- **Cross-module event subscriptions** — discovery detects which modules import event
  types, but does not model subscription routing
- **Circular dependencies** — not explicitly detected; will be added if needed
- **Custom validation rules** — not yet supported; extend `BoundaryValidator` for custom
  checks
