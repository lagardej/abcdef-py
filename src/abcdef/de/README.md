# `abcdef.de`

Event-sourced extensions that build on the DDD model from `abcdef.d`.

## Purpose

`abcdef.de` adds event-sourcing mechanics to the abstractions from
`abcdef.d`. It provides event-sourced aggregates, append-only event storage,
aggregate state snapshots, and repositories that rehydrate aggregates from
history.

This package is the bridge between DDD and event sourcing. It is not meant to
replace the domain model in `abcdef.d`.

## Internal Dependencies

`abcdef.de` depends on:

- `abcdef.b`
- `abcdef.d`

## Public Imports

Import from the package facade, for example
`from abcdef.de import EventSourcedAggregate`.

Public exports include:

- `AggregateRecord`, `AggregateRegistry`, `AggregateState`
- `AggregateStore`, `EventStore`, `VersionConflictError`
- `EventSourcedAggregate`, `EventSourcedRepository`
- `EventSourcedDomainEvent`, `EventSourcedDomainEventRegistry`

## Key Concepts

- `EventSourcedAggregate` — aggregate rebuilt from event history
- `EventStore` — append-only store of emitted events
- `AggregateStore` — state snapshots for replay optimisation
- `AggregateState` — persisted state boundary for an aggregate
- `EventSourcedRepository` — coordinates replay and persistence
- `VersionConflictError` — optimistic concurrency failure signal

## Use When

- you want event sourcing as the source of truth
- you need append-only domain history and replayable state
- you want to optimise replay with stored aggregate state

## Do Not Use For

- defining foundational domain concepts that are not event-sourcing specific
- bypassing the aggregate model in `abcdef.d`
- query-side projections or read-model storage

## See Also

- [Package reference](../README.md)
- [`abcdef.d`](../d/README.md)
- [`abcdef.c`](../c/README.md)
- [`abcdef.in_memory`](../in_memory/README.md)

