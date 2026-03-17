# `abcdef.b`

Shared foundational primitives for the rest of `abcdef`.

## Purpose

`abcdef.b` defines the smallest common building blocks used across the
framework: messages, events, results, and class registries.

This package is the foundation layer. Other public bricks build on it.

## Internal Dependencies

`abcdef.b` has no dependency on other `abcdef` subpackages.

## Public Imports

Import from the package facade:

```python
from abcdef.b import ClassRegistry, Event, Message, Result
```

## Key Concepts

- `Message` — common root for commands, queries, and events
- `Event` — immutable record of something that happened
- `Result` — marker type for operation outcomes
- `ClassRegistry` — stable key-to-class registry for persisted identifiers

## Use When

- you need shared abstractions with no CQRS or DDD commitment yet
- you need a common base type for message dispatch
- you need stable class registration for persistence or deserialisation

## Do Not Use For

- domain modelling concerns such as aggregates or value objects
- CQRS buses, handlers, or documents
- event-sourcing mechanics

## See Also

- [Package reference](../README.md)
- [`abcdef.c`](../c/README.md)
- [`abcdef.d`](../d/README.md)

