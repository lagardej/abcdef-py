# `abcdef.in_memory`

In-memory adapters for testing, examples, and lightweight local runs.

## Purpose

`abcdef.in_memory` provides concrete in-memory implementations of selected framework
abstractions. These adapters are useful for tests, spikes, and local composition where
durability and external infrastructure are unnecessary.

This package is adapter infrastructure. It is not part of the conceptual core model of
CQRS, DDD, or event sourcing.

## Internal Dependencies

`abcdef.in_memory` depends on:

- `abcdef.b`
- `abcdef.c`
- `abcdef.d`
- `abcdef.de`

## Public Imports

Import from the package facade, for example
`from abcdef.in_memory import InMemoryRepository`.

Public exports include:

- `InMemoryRepository`
- `InMemoryDocumentStore`
- `InMemoryEventBus`
- `InMemoryEventStore`
- `InMemoryAggregateStore`

## Key Concepts

- `InMemoryRepository` — dict-backed repository for aggregates
- `InMemoryDocumentStore` — dict-backed document store for read models
- `InMemoryEventBus` — synchronous in-process event fan-out
- `InMemoryEventStore` — append-only event storage in memory
- `InMemoryAggregateStore` — in-memory aggregate state snapshots

## Use When

- writing tests without external infrastructure
- prototyping composition roots and example applications
- validating flows before choosing production adapters

## Do Not Use For

- durable persistence
- inter-process messaging or asynchronous delivery guarantees
- production scenarios that need scaling, recovery, or operational controls

## See Also

- [Package reference](../README.md)
- [`abcdef.c`](../c/README.md)
- [`abcdef.d`](../d/README.md)
- [`abcdef.de`](../de/README.md)
