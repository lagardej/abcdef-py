# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

*(none)*

---

## Tasks

- **No `DomainService` base class** — The `domain_service` marker exists but has no corresponding base class. All
  other markers have base classes (`Command`, `Query`, `Result`, `Document`, `AggregateRoot`, `ValueObject`, `Event`).
  Add a `DomainService` base class in `core/d/`.

- **No `Specification` base class** — Same as above. The `specification` marker exists with no base class.
  Add a `Specification` base class in `core/d/`.

- **`EventSourcedRepository.find_all()` contract is unclear** — It raises `NotImplementedError` with a message
  suggesting projections. But subclasses inheriting from `Repository` expect to override it. Either formally remove
  it from the `EventSourcedRepository` contract (document it as unsupported) or clarify the intended override
  pattern.

- **`EventSourcedRepository` does not publish events post-commit** — After `save()`, committed events are discarded
  and never published to an `EventBus`. Projectors have no way to react in real time. Wire the repository to publish
  events after appending them to the event store.

---

## Improvements

- **Introduce `EventEmittingAggregate` in `d/`** — Base class for aggregates that emit domain events without event
  sourcing. `EventSourcedAggregate` in `de/` would extend it. This cleanly separates "aggregate that raises events
  for the bus" from "aggregate whose state is sourced from events". `DomainEvent` would move to `d/` as the event
  type emitted by such aggregates. Deliberately deferred until a concrete use case exists.

- **`build_from_events()` and `_create_from_state()` should be `@abstractmethod`** — Both raise `NotImplementedError`
  in `EventSourcedRepository` but are not declared abstract. A subclass that forgets to implement them is only caught
  at runtime, not at instantiation. Declare them abstract.

- **`AggregateState` has no enforced structure** — It is a bare marker class. Subclasses carry all state as plain
  attributes with no enforced structure. A frozen dataclass base or convention would make state classes more
  predictable and serialisation-friendly.

- **ES aggregate events are untyped** — `EventSourcedAggregate._emit_event(event: object)` accepts `object`, while
  `DomainEvent` is now a typed base. Tighten `_emit_event` to accept `DomainEvent`, and update the `de/` test
  fixtures accordingly.

- **`ValueObject` immutability is documented but not enforced** — The docstring says "use frozen dataclasses or
  similar" but nothing prevents mutation. Either drop the suggestion and document the limitation honestly, or
  provide a `FrozenValueObject` that enforces immutability via `__setattr__` protection, as `AggregateId` does.

- **`AggregateId.__repr__` is not tested** — All other `AggregateId` behaviours are covered. Add a test for
  `__repr__`.

- **`get_all_events()` ordering guarantee is undocumented** — `InMemoryEventStore` preserves insertion order across
  aggregates, which is correct for in-memory use. A persistent backend may not guarantee this. Document the expected
  ordering contract in the `EventStore` ABC so implementations know what to honour.

- **`in_memory/` tests have no shared `fixtures.py`** — `de/` and `c/` test directories use `fixtures.py` for
  shared setup. `in_memory/` tests inline their fixture setup. Extract a `fixtures.py` for consistency.

- **Document `_abstract_event` convention in `architecture.md`** — The `_abstract_event = True` flag on `DomainEvent`
  is an internal convention for exempting intermediate base classes from the `event_type` enforcement in
  `Event.__init_subclass__`. Document it alongside the marker attribute naming decisions.
