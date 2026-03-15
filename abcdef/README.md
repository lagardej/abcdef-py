# ABCDEF — A Basic CQRS, DDD, Event-Sourcing Framework

Minimal framework providing the plumbing for event-sourced, domain-driven applications using CQRS patterns.

## Structure

```
abcdef/
├── core/              # Abstract base classes and marker interfaces
│   ├── c/             # CQRS — commands, queries, handlers, buses, registries
│   ├── d/             # DDD — aggregates, value objects, repositories
│   ├── de/            # DDD + ES — event-sourced aggregates, stores, repositories
│   ├── cde/           # CQRS + DDD + ES — Event base class
│   └── markers.py     # Shared marker inspection utility (_get_marker)
├── specification/     # Specification pattern — Specification ABC and combinators
└── in_memory/         # In-memory implementations for testing and development
```

## Core Concepts

Each concept lives in the `core/` sub-package matching its paradigm intersection — CQRS (`c/`),
DDD (`d/`), both plus Event Sourcing (`de/`, `cde/`):

| Package | Paradigms | Contents |
|---------|-----------|----------|
| `c/` | CQRS | `Command`, `Query`, handlers, buses, registries, `Result`, `Document`, `DocumentStore` |
| `d/` | DDD | `AggregateRoot`, `AggregateId`, `ValueObject`, `Repository` |
| `de/` | DDD + ES | `EventSourcedAggregate`, `EventStore`, `AggregateStore`, `EventSourcedRepository`, `Snapshot` |
| `cde/` | CQRS + DDD + ES | `Event` |
| `specification/` | DDD | `Specification` ABC, `&`/`\|`/`~` combinators, `@specification` marker |

- **Command** — Intent to mutate state; handled by exactly one `CommandHandler`
- **Query** — Request to read state; handled by exactly one `QueryHandler`
- **Event** — Immutable record of something that happened in the domain
- **AggregateRoot** — Entity that maintains invariants and emits events
- **ValueObject** — Immutable, identity-free object compared by value
- **Repository** — Abstracts persistence; loads and saves aggregates
- **EventStore** — Append-only store; single source of truth for event sourcing
- **AggregateStore** — Persists aggregate state records for replay optimisation
- **EventSourcedAggregate** — Aggregate with version tracking and event application
- **EventSourcedRepository** — Orchestrates event replay and state persistence strategy
- **MessageBus / CommandBus / QueryBus / EventBus** — Publish/subscribe infrastructure
- **Document** — Denormalised, query-optimised read model built from domain events
- **DocumentStore** — Query-side persistence; counterpart to `Repository` on the write side
- **Projector** — Subscribes to domain events and updates Documents in a DocumentStore
- **Specification** — Reusable business rule predicate; composable via `&`, `|`, and `~`

## Architecture Markers

Each paradigm package exposes decorators for runtime annotation:

| Marker | Package | Attribute set |
|--------|---------|---------------|
| `@command`, `@query`, `@command_handler`, `@query_handler`, `@document`, `@document_store`, `@projector` | `c/` | `__cqrs_type__` |
| `@aggregate`, `@value_object`, `@repository`, `@domain_service`, `@factory`, `@identifier` | `d/` | `__ddd_type__` |
| `@specification` | `specification/` | `__ddd_type__` |
| `@event` | `cde/` | `__cqrs_type__` |

`_get_marker(cls, attr)` (from `core/markers.py`) inspects a class or its parents for a marker attribute.

## Event Sourcing

- Event store is append-only — events are never modified or deleted
- Aggregates are rebuilt by replaying events from the event store
- State records capture aggregate state at a version boundary for performance
- Delta replay: load latest state record, replay only events after its version
- `EventSourcedAggregate` exposes framework-internal methods prefixed with `_`
  (`_get_uncommitted_events`, `_mark_events_as_committed`, `_mark_state_saved`,
  `_load_from_history`) — called by the repository, not by domain code
- Projectors consume events and write Documents; Documents are never derived
  from the event store directly
