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

- **`Specification` as its own module** — The specification pattern has a real interface (`is_satisfied_by`),
  combinators (`and`, `or`, `not`), and enough structure to warrant a dedicated package rather than a stub in
  `core/`. Model after the Java reference implementation.

- **`ValueObject` immutability is documented but not enforced** — The docstring says "use frozen dataclasses or
  similar" but nothing prevents mutation. Either drop the suggestion and document the limitation honestly, or
  provide a `FrozenValueObject` that enforces immutability via `__setattr__` protection, as `AggregateId` does.

- **`AggregateId.__repr__` is not tested** — All other `AggregateId` behaviours are covered. Add a test for
  `__repr__`.

- **Document `_abstract_event` convention in `architecture.md`** — The `_abstract_event = True` flag on `DomainEvent`
  is an internal convention for exempting intermediate base classes from the `event_type` enforcement in
  `Event.__init_subclass__`. Document it alongside the marker attribute naming decisions.
