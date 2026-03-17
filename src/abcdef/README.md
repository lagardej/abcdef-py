# ABCDEF — A Basic CQRS, DDD, Event-Sourcing Framework

Technical package reference for `abcdef`.

For the project overview, project goals, and development workflow, see the
[root README](../../README.md).

Minimal framework providing the plumbing for
[event-sourced](https://martinfowler.com/eaaDev/EventSourcing.html),
[domain-driven](https://martinfowler.com/bliki/DomainDrivenDesign.html) applications
using [CQRS](https://martinfowler.com/bliki/CQRS.html) patterns.

Each paradigm is independent. `d/` provides aggregates, value objects, and repositories
with no knowledge of event sourcing or CQRS. `c/` provides commands, queries, and buses
with no knowledge of the domain model. `de/` is the glue: it extends `d/` with event
sourcing mechanics and wires aggregates to the event store. Use only what you need —
aggregates without event sourcing, CQRS without DDD, or all three together.

Shared foundational primitives live in `b/` (Event, Message, Result, ClassRegistry) and
are used by the rest of the framework. `in_memory/` provides lightweight implementations
of every store and bus for use in tests and development. `specification/` provides a
composable predicate pattern for expressing business rules; it integrates naturally with
`d/` aggregates and repositories but has no dependency on any other package.

## Structure

```
abcdef/
├── markers.py         # Shared marker inspection utility (_get_marker)
├── b/                 # Basic primitives: Event, Message, Result, ClassRegistry
├── c/                 # CQRS — commands, queries, handlers, buses, registries
├── d/                 # DDD — aggregates, value objects, repositories
├── de/                # DDD + ES — event-sourced aggregates, stores, repositories
├── in_memory/         # In-memory implementations for testing and development
└── specification/     # Specification pattern — Specification ABC and combinators
```

## Per-Brick Guides

Each public subpackage has a focused guide describing its purpose, dependencies, public
imports, and intended usage:

- [`b/`](b/README.md) — shared foundational primitives
- [`c/`](c/README.md) — CQRS building blocks
- [`d/`](d/README.md) — DDD building blocks
- [`de/`](de/README.md) — event-sourced DDD extensions
- [`in_memory/`](in_memory/README.md) — in-memory adapters
- [`specification/`](specification/README.md) — specification pattern

## Core Concepts

Each concept lives in its package (`c/`, `d/`, `de/`, etc.). Shared primitives live in
`b/`:

| Package | Paradigms | Contents |
|------------------|-----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `b/` | Shared | `Event`, `Message`, `Result`, `ClassRegistry` | | `c/` | CQRS |
`Command`, `CommandHandler`, `Query`, `QueryHandler`, `MessageBus` / `CommandBus` /
`QueryBus` / `EventBus`, `Document`, `DocumentStore`, `Projector` | | `d/` | DDD |
`AggregateRoot`, `AggregateId`, `EventEmittingAggregate`, `DomainEvent`,
`DomainEventRegistry`, `ValueObject`, `Repository` | | `de/` | DDD + ES |
`EventSourcedAggregate`, `AggregateState`, `EventStore`, `AggregateStore`,
`EventSourcedRepository`, `EventSourcedDomainEvent`, `AggregateRegistry`,
`EventSourcedDomainEventRegistry` | | `in_memory/` | Implementations |
`InMemoryRepository`, `InMemoryDocumentStore`, `InMemoryEventBus`, `InMemoryEventStore`,
`InMemoryAggregateStore` | | `specification/` | — | `Specification` ABC, `&`/`\|`/`~`
combinators, `@specification` marker |

<a id="event"></a>

- **Event** — Immutable record of something that happened in the domain
  <a id="message"></a>
- **Message** — Common root type for Commands, Queries, and Events; buses and handlers
  constrain against this type <a id="result"></a>
- **Result** — Marker interface for the outcome of an operation, returned by command and
  query handlers <a id="classregistry"></a>
- **ClassRegistry** — Generic registry mapping stable string keys to classes; decouples
  persisted identifiers from Python class names so classes can be renamed freely without
  invalidating stored data

<a id="command"></a>

- **Command** — Intent to mutate state; handled by exactly one `CommandHandler`
  <a id="commandhandler"></a>
- **CommandHandler** — Processes a single Command type; orchestrates changes to
  aggregates and emits domain events <a id="query"></a>
- **Query** — Request to read state; handled by exactly one `QueryHandler`
  <a id="queryhandler"></a>
- **QueryHandler** — Processes a single Query type; reads from document stores and
  returns a Result <a id="messagebus"></a>
- **MessageBus / CommandBus / QueryBus / EventBus** — Publish/subscribe infrastructure
  <a id="document"></a>
- **Document** — Denormalised, query-optimised read model built from domain events
  <a id="documentstore"></a>
- **DocumentStore** — Query-side persistence; counterpart to `Repository` on the write
  side <a id="projector"></a>
- **Projector** — Subscribes to domain events and updates Documents in a DocumentStore

<a id="aggregateroot"></a>

- **AggregateRoot** — Entity that maintains invariants and emits events
  <a id="aggregateid"></a>
- **AggregateId** — Infrastructure-level identity for an aggregate; decouples
  persistence mechanics from domain identity <a id="eventemittingaggregate"></a>
- **EventEmittingAggregate** — Aggregate that records domain events for publication on
  the bus; state is managed directly, not derived from events <a id="domainevent"></a>
- **DomainEvent** — An Event raised by a domain aggregate; extends Event for dispatch on
  an EventBus <a id="domaineventregistry"></a>
- **DomainEventRegistry** — Registry of DomainEvent subclasses keyed by `event_type`;
  decouples deserialisation from Python class names <a id="valueobject"></a>
- **ValueObject** — Immutable, identity-free object compared by value
  <a id="repository"></a>
- **Repository** — Abstracts persistence; loads and saves aggregates

<a id="aggregatestate"></a>

- **AggregateState** — Immutable snapshot of an aggregate's data at a version boundary;
  used for replay optimisation <a id="eventsourceddomainevent"></a>
- **EventSourcedDomainEvent** — A DomainEvent raised by an event-sourced aggregate;
  carries the aggregate instance identity alongside the event data
  <a id="aggregateregistry"></a>
- **AggregateRegistry** — Registry of EventSourcedAggregate subclasses keyed by
  `aggregate_type`; decouples rehydration from Python class names
  <a id="eventsourceddomaineventregistry"></a>
- **EventSourcedDomainEventRegistry** — Registry of EventSourcedDomainEvent subclasses
  keyed by `event_type`; decouples deserialisation from Python class names
  <a id="eventstore"></a>
- **EventStore** — Append-only store; single source of truth for event sourcing
  <a id="aggregatestore"></a>
- **AggregateStore** — Persists aggregate state records for replay optimisation and
  enforces optimistic concurrency (expected_version / VersionConflictError)
  <a id="eventsourcedaggregate"></a>
- **EventSourcedAggregate** — Aggregate with version tracking and event application
  <a id="eventsourcedrepository"></a>
- **EventSourcedRepository** — Orchestrates event replay and state persistence strategy

<a id="specification"></a>

- **Specification** — Reusable business rule predicate; composable via `&`, `|`, and `~`

## Class Hierarchies

### Messages

```
Message
├── Command
│   └── (CommandHandler processes one Command type)
├── Query
│   └── (QueryHandler processes one Query type)
└── Event
    └── DomainEvent
        └── EventSourcedDomainEvent
```

`Message` · `Command` · `CommandHandler` · `Query` · `QueryHandler` · `Event` ·
`DomainEvent` · `EventSourcedDomainEvent`

### Aggregates

```
AggregateRoot
└── EventEmittingAggregate
    └── EventSourcedAggregate
```

`AggregateRoot` · `EventEmittingAggregate` · `EventSourcedAggregate`

## Architecture Markers

### Value & Identity types

```
ValueObject
AggregateId
```

- `ValueObject` — frozen dataclass base for immutable value types. These are compared by
  value and have no identity semantics.
- `AggregateId` — base identity type for aggregates; used by repositories and stores to
  identify aggregate instances.

Note: `ValueObject` and `AggregateId` are standalone base types in the framework and do
not form a deeper subclass tree in the core package; they are intended as simple
building blocks for domain models.

Each paradigm package exposes decorators for runtime annotation:

| Marker | Package | Attribute set |
|----------------------------------------------------------------------------------------------------------|------------------|-----------------|
| `@command`, `@query`, `@command_handler`, `@query_handler`, `@document`,
`@document_store`, `@projector` | `c/` | `__cqrs_type__` | | `@aggregate`,
`@value_object`, `@repository`, `@domain_service`, `@factory`, `@identifier` | `d/` |
`__ddd_type__` | | `@event_store`, `@aggregate_store` | `de/` | `__de_type__` | |
`@specification` | `specification/` | `__specification_type__` |

`_get_marker(cls, attr)` (from `abcdef/markers.py`) inspects a class or its parents for
a marker attribute.

## Public API Boundaries

- Import each package from its own namespace (`abcdef.b`, `abcdef.c`, `abcdef.d`,
  `abcdef.de`, `abcdef.in_memory`, `abcdef.specification`).
- Package `__init__.py` facades only re-export symbols from their own package namespace.
- Cross-package usage should import from the package that defines the symbol (for
  example, `Event` from `abcdef.b`, not from `abcdef.d`).
- The shared marker inspection utility lives at `abcdef.markers` (package root), not
  inside any sub-package.

## Event Sourcing

- Event store is append-only — events are never modified or deleted
- Aggregates are rebuilt by replaying events from the event store
- State records capture aggregate state at a version boundary for performance
- Delta replay: load the latest state record, replay only events after its version
- `EventSourcedAggregate` exposes framework-internal methods prefixed with `_`
  (`_get_uncommitted_events`, `_mark_events_as_committed`, `_mark_state_saved`,
  `_load_from_history`) — called by the repository, not by domain code
- Projectors consume events and write Documents; Documents are never derived from the
  event store directly
