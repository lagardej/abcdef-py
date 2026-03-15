# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

*(none)*

---

## Tasks

- **`Event` has no base fields** — The `Event` marker class carries no `aggregate_id`, no `occurred_at` timestamp,
  and no `event_type` discriminator. Projections consuming `get_all_events()` have no guaranteed fields to work with.
  Define a minimal set of base fields on `Event`.

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

- **`build_from_events()` and `_create_from_state()` should be `@abstractmethod`** — Both raise `NotImplementedError`
  in `EventSourcedRepository` but are not declared abstract. A subclass that forgets to implement them is only caught
  at runtime, not at instantiation. Declare them abstract.

- **`AggregateState` has no enforced structure** — It is a bare marker class. Subclasses carry all state as plain
  attributes with no enforced structure. A frozen dataclass base or convention would make state classes more
  predictable and serialisation-friendly.

- **ES aggregate events are untyped** — `EventSourcedAggregate._emit_event(event: object)` accepts `object`, while
  `Event` is a typed marker. The two event concepts are decoupled. `_emit_event` should accept `Event`, and
  event-sourced aggregate events should extend `Event`, converging the two concepts.

- **`ValueObject` immutability is documented but not enforced** — The docstring says "use frozen dataclasses or
  similar" but nothing prevents mutation. Either drop the suggestion and document the limitation honestly, or
  provide a `FrozenValueObject` that enforces immutability via `__setattr__` protection, as `AggregateId` does.

- **`AggregateId.__repr__` is not tested** — All other `AggregateId` behaviours are covered. Add a test for
  `__repr__`.

- **Marker attribute naming is implicit** — CQRS markers set `__cqrs_type__`, DDD markers set `__ddd_type__`, but
  the `event` marker in `cde/` sets `__cqrs_type__` rather than a `__cde_type__`. This is not wrong but looks
  accidental. Document the decision explicitly in `architecture.md`.

- **`get_all_events()` ordering guarantee is undocumented** — `InMemoryEventStore` preserves insertion order across
  aggregates, which is correct for in-memory use. A persistent backend may not guarantee this. Document the expected
  ordering contract in the `EventStore` ABC so implementations know what to honour.

- **`in_memory/` tests have no shared `fixtures.py`** — `de/` and `c/` test directories use `fixtures.py` for
  shared setup. `in_memory/` tests inline their fixture setup. Extract a `fixtures.py` for consistency.
