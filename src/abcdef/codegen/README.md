# `abcdef.codegen` — Scaffolding Tool

`abcdef.codegen` generates boilerplate directory trees and stub files for applications
built on the ABCDEF framework. It removes the busywork of creating new modules and
features by hand and ensures the generated scaffolding is architecturally correct from
the start.

## CLI

After `uv sync`, the `abcdef-gen` command is available on `PATH`:

```
abcdef-gen module <name> --type command|query [--interfaces INTERFACE ...] [--root PATH]
abcdef-gen feature <module> <use-case> [--interfaces INTERFACE ...] [--root PATH]
```

`--root` defaults to the current working directory.

`--interfaces` accepts one or more of `cli`, `web`, `api` (default: `cli`):

- `cli` — command-line handler stub
- `web` — server-side HTML handler stub
- `api` — JSON/REST handler stub

## Commands

### `module` — scaffold a new module

Creates a full directory tree for a new command or query module:

```
abcdef-gen module orders --type command --root src/myapp
abcdef-gen module orders --type command --interfaces cli web api --root src/myapp
```

Creates under `src/myapp/orders/`:

```
__init__.py               # __modularity__ dict + __all__ = []
domain/orders.py          # AggregateRoot + AggregateId skeleton
domain/orders_repository.py  # Repository interface
application/placeholder.py   # Command + CommandHandler stub
infrastructure/placeholder.py  # TODO comment for concrete implementations
interface/cli/placeholder.py   # CLI function stub        (if cli selected)
interface/web/placeholder.py   # Web handler stub         (if web selected)
interface/api/placeholder.py   # API handler stub         (if api selected)
```

For `--type query`:

```
__init__.py               # __modularity__ dict + __all__ = []
projection/reports.py     # Document (read model) skeleton
application/placeholder.py   # Query + QueryHandler stub
infrastructure/placeholder.py  # TODO comment
interface/cli/placeholder.py   # CLI stub    (if cli selected)
interface/web/placeholder.py   # Web stub    (if web selected)
interface/api/placeholder.py   # API stub    (if api selected)
```

Refuses with an error if the module directory already exists.

### `feature` — add a use case to an existing module

Adds files to a module that already exists on disk:

```
abcdef-gen feature orders create_order --root src/myapp
abcdef-gen feature orders create_order --interfaces web api --root src/myapp
```

Creates:

```
orders/application/create_order.py         # Command + CommandHandler (or Query + QueryHandler)
orders/interface/cli/create_order.py       # CLI stub    (if cli selected)
orders/interface/web/create_order.py       # Web stub    (if web selected)
orders/interface/api/create_order.py       # API stub    (if api selected)
```

The module type (`command` or `query`) is inferred from the existing `__init__.py`
`__modularity__` dict — no flag needed. Refuses if any target file already exists.

`__init__.py` is never modified — export wiring is left to the developer.

## Python API

```python
from pathlib import Path
from abcdef.codegen import generate_module, generate_feature
from abcdef.modularity.markers import COMMAND_MODULE

# Default: cli only
created = generate_module("orders", COMMAND_MODULE, Path("src/myapp"))

# Multiple interfaces
created = generate_module(
    "orders", COMMAND_MODULE, Path("src/myapp"),
    interfaces=["cli", "web", "api"],
)

created = generate_feature(
    "orders", "create_order", Path("src/myapp"),
    interfaces=["web", "api"],
)
```

Both functions return a list of `Path` objects for the files they created.

## Anti-drift guarantee

Generated scaffolding is validated in the test suite against `abcdef.modularity`:

```python
modularity = Modularity(tmp_path)
modularity.discover()
assert modularity.validate() == []
```

If a template falls out of sync with the architecture rules, CI catches it.

## What is not generated

- No modifications to existing `__init__.py` (export wiring is a domain decision)
- No wiring into a composition root
- No event definitions or inter-module bindings
- No test stubs
