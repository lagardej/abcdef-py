# `abcdef.d`

Domain-driven design building blocks for aggregates, value objects,
repositories, and domain events.

## Purpose

`abcdef.d` contains the core DDD abstractions used to model domain behaviour.
It is the package where aggregates enforce invariants, domain events express
business facts, and repositories abstract persistence.

This package is domain-focused. It does not know about CQRS buses or
event-sourcing storage.

## Internal Dependencies

`abcdef.d` depends on:

- `abcdef.b`

## Public Imports

Import from the package facade, for example
`from abcdef.d import AggregateRoot`.

Public exports include:

- `AggregateId`, `AggregateRoot`, `EventEmittingAggregate`
- `DomainEvent`, `DomainEventRegistry`
- `Repository`, `ValueObject`

## Key Concepts

- `AggregateRoot` — entity that protects invariants
- `AggregateId` — infrastructure-level identity abstraction
- `EventEmittingAggregate` — aggregate that records domain events
- `DomainEvent` — business event emitted by an aggregate
- `Repository` — abstraction for loading and saving aggregates
- `ValueObject` — immutable, identity-free concept compared by value

## Use When

- you want a domain model with explicit aggregates and value objects
- you need repository abstractions without choosing a storage strategy yet
- you want domain events without full event sourcing

## Do Not Use For

- command/query buses or projection infrastructure
- event-store append and replay mechanics
- leaking infrastructure concerns into domain behaviour

## See Also

- [Package reference](../README.md)
- [`abcdef.b`](../b/README.md)
- [`abcdef.de`](../de/README.md)
- [`abcdef.specification`](../specification/README.md)

