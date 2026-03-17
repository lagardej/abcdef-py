# `abcdef.c`

CQRS building blocks for commands, queries, handlers, buses, and read models.

## Purpose

`abcdef.c` provides the plumbing for Command Query Responsibility Segregation. It
defines write-side commands, read-side queries, handler abstractions, message buses, and
document-side read-model support.

This package is about coordination and read/write separation. It is not a package for
domain modelling.

## Internal Dependencies

`abcdef.c` depends on:

- `abcdef.b`

## Public Imports

Import from the package facade, for example `from abcdef.c import Command`.

Public exports include:

- `Command`, `CommandHandler`, `CommandRegistry`
- `Query`, `QueryHandler`, `QueryRegistry`
- `MessageBus`, `CommandBus`, `QueryBus`, `EventBus`
- `Document`, `DocumentStore`, `Projector`

## Key Concepts

- `Command` / `CommandHandler` — write-side intent and orchestration
- `Query` / `QueryHandler` — read-side requests and results
- `MessageBus`, `CommandBus`, `QueryBus`, `EventBus` — dispatch infrastructure
- `Document` / `DocumentStore` — query-optimised read models
- `Projector` — updates documents in response to events

## Use When

- you want explicit separation between writes and reads
- you need bus abstractions for commands, queries, or events
- you want projection-based read models

## Do Not Use For

- aggregates, value objects, or repositories
- event-store concerns or replay mechanics
- embedding domain behaviour into handlers or projectors

## See Also

- [Package reference](../README.md)
- [`abcdef.b`](../b/README.md)
- [`abcdef.d`](../d/README.md)
- [`abcdef.de`](../de/README.md)
