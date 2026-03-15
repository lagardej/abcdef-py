# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

*(none)*

---

## Tasks

*(none)*

---

## Improvements

- **Introduce `EventEmittingAggregate` in `d/`** — Base class for aggregates that emit domain events without event
  sourcing. `EventSourcedAggregate` in `de/` would extend it. This cleanly separates "aggregate that raises events
  for the bus" from "aggregate whose state is sourced from events". `DomainEvent` would move to `d/` as the event
  type emitted by such aggregates. Deliberately deferred until a concrete use case exists.
