# ABCDEF — A Basic CQRS, DDD, Event-Sourcing Framework

ABCDEF is a lightweight Python framework with building blocks for
[CQRS](https://martinfowler.com/bliki/CQRS.html),
[domain-driven design](https://martinfowler.com/bliki/DomainDrivenDesign.html),
and [event sourcing](https://martinfowler.com/eaaDev/EventSourcing.html).

Each paradigm is independent. `abcdef.d` provides aggregates, value objects,
and repositories with no knowledge of event sourcing or CQRS. `abcdef.c`
provides commands, queries, and buses with no knowledge of the domain model.
`abcdef.de` is the glue: it extends `abcdef.d` with event-sourcing mechanics
and wires aggregates to the event store. Use only what you need — DDD without
event sourcing, CQRS without DDD, or all three together.

## Purpose

ABCDEF provides reusable primitives and abstractions so applications can focus on domain behaviour instead of framework
wiring.

Core package areas:

- `abcdef.b` - base primitives (event/message/registry/result)
- `abcdef.c` - CQRS building blocks
- `abcdef.d` - DDD building blocks
- `abcdef.de` - event-sourced DDD integration
- `abcdef.in_memory` - in-memory adapters for tests and local runs
- `abcdef.specification` - specification pattern support
- `abcdef.modularity` - modular architecture validation and documentation

## How to choose a brick

Start with the smallest brick that matches your needs, then add others only
when the architecture requires them.

| If you want...                                                                 | Use...                   | Notes                                                                       |
|--------------------------------------------------------------------------------|--------------------------|-----------------------------------------------------------------------------|
| Shared message and event primitives                                            | `abcdef.b`               | Foundation layer used by the rest of the framework                          |
| A domain model with aggregates, value objects, repositories, and domain events | `abcdef.d`               | DDD only; no CQRS or event-sourcing mechanics                               |
| Event sourcing on top of the DDD model                                         | `abcdef.de` + `abcdef.d` | `abcdef.de` extends `abcdef.d`; use it when events are your source of truth |
| Commands, queries, buses, and read models                                      | `abcdef.c`               | CQRS plumbing; can be used with or without DDD                              |
| Reusable business-rule predicates                                              | `abcdef.specification`   | Small standalone brick; fits naturally with `abcdef.d`                      |
| Lightweight adapters for tests, examples, and local runs                       | `abcdef.in_memory`       | In-memory implementations for `c`, `d`, and `de` abstractions               |
| Validation and documentation of modular application structure                  | `abcdef.modularity`        | For application developers to enforce and document module boundaries        |

Typical combinations:

- `abcdef.d` for DDD without event sourcing
- `abcdef.d` + `abcdef.de` for event-sourced domain models
- `abcdef.c` + `abcdef.d` when you want CQRS around a DDD model
- `abcdef.c` + `abcdef.d` + `abcdef.de` for CQRS with event-sourced aggregates
- `abcdef.in_memory` alongside any of the above for testing and local composition

## Package Reference

The canonical project overview lives in this README. The detailed package
reference lives in [`src/abcdef/README.md`](src/abcdef/README.md), including:

- package structure
- core concepts and class hierarchies
- architecture markers
- public API boundaries
- event-sourcing notes

Each public brick also has its own focused guide:

- [`abcdef.b`](src/abcdef/b/README.md) — shared foundational primitives
- [`abcdef.c`](src/abcdef/c/README.md) — CQRS building blocks
- [`abcdef.d`](src/abcdef/d/README.md) — DDD building blocks
- [`abcdef.de`](src/abcdef/de/README.md) — event-sourced DDD extensions
- [`abcdef.in_memory`](src/abcdef/in_memory/README.md) — in-memory adapters
- [`abcdef.specification`](src/abcdef/specification/README.md) — specification pattern
- [`abcdef.modularity`](src/abcdef/modularity/README.md) — modular architecture validation and documentation

---

## Project Goals

ABCDEF is a Python port of a private Java library of the same purpose. Beyond the port itself, this project is also a
**learning exercise for AI-assisted development in an unfamiliar language:** the AI helped translate idioms from Java to
Python, catch design errors, and generate implementations and documentation.

Roles are divided as follows:

| Role      | Responsibilities                                                     |
|-----------|----------------------------------------------------------------------|
| Developer | Overall architecture, design, and feature decisions                  |
| AI agent  | Ports from Java, generates implementations, refactors, and documentation; flags design issues |

---

## Development

Common tasks are available as Make targets. Run `make` or `make help` for the full list.

```
make check-format  check formatting without modifying files
make check-types   run pyright type checker
make lint          run ruff linter without modifying files
make test          run pytest with coverage

make fix           auto-fix lint violations then format
make format        auto-format source files

make ci            run check-format, lint, check-types, test
make mutate        run mutation tests (mutmut)

make install       install git hooks
```

### Verbosity

`test` and `ci` support a `V` variable controlling output detail:

| `V` | Level   | Behaviour                                 |
|-----|---------|-------------------------------------------|
| `0` | quiet   | dots and failures only                    |
| `1` | default | file-level progress (default if omitted)  |
| `2` | verbose | per-test names, full tracebacks           |

```
make test V=0
make ci V=2
```

`check-format`, `check-types`, `lint`, `fix`, `format`, and `mutate` are unaffected — they already only print what is relevant.

### Logs

`test`, `ci`, and `mutate` tee output to timestamped log files under `logs/`:

```
logs/test-20260314-074744.log
logs/ci-20260314-074814.log
logs/mutate-20260314-075001.log
```

`logs/test.log`, `logs/ci.log`, and `logs/mutate.log` are symlinks that always point to the latest run.
