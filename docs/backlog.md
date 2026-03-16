# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

- **`de/event_sourced_repository.py` — `assert` used for a storage invariant**
  `get_by_id` uses `assert record is not None` to guard against events existing
  without a matching aggregate record. `assert` is silently dropped under
  `-O` / `PYTHONOPTIMIZE=1`, so this check disappears in optimised builds.
  Replace with `raise RuntimeError(...)` (or a dedicated `StorageFaultError`)
  so the invariant is enforced unconditionally.

---

## Tasks

(none)

---

## Improvements

- **`de/event_sourced_repository.py` — non-transactional write order
  undocumented**
  The aggregate store write and the event store append are two separate,
  non-atomic operations. If `append_events` raises after
  `aggregate_store.save` succeeds, the version record is advanced but no events
  are stored, leaving the aggregate unreconstructable. The `save()` docstring
  should state explicitly that these writes are not transactional and describe
  what partial failure means for the caller.

- **`de/event_sourced_aggregate.py` — `from_state` return type too wide;
  downstream `# type: ignore` unexplained**
  `from_state` is annotated to return `EventSourcedAggregate[TState]` rather
  than `Self`, which is a Python limitation with generic classmethods. The
  `# type: ignore[return-value]` in `event_sourced_repository.py:get_by_id` is
  a direct consequence. Add a comment on `from_state` explaining the constraint,
  and update the ignore comment in the repository to reference it.

- **`de/markers.py` — `AggregateStore` has no architecture marker**
  Every other major base class in the framework carries a marker. `AggregateStore`
  has no `__de_type__`. Either add an `@aggregate_store` decorator to
  `de/markers.py` and apply it, or explicitly document why it is intentionally
  unmarked.

- **`c/command.py`, `c/query.py` — dead `TypeVar` exports pollute public API**
  `TCommand`, `TResult`, `TQuery`, `TQueryResult` are defined as old-style
  `TypeVar` objects at module level and re-exported from `c/__init__.py`.
  `CommandHandler` and `QueryHandler` already use PEP 695 generic syntax and
  do not reference these variables. Remove the declarations and drop them from
  `__all__`.

- **`d/repository.py` — dead `TypeVar` declarations**
  `TId` and `TAggregate` are defined at module level but never used; `Repository`
  uses PEP 695 generics directly. Remove them.

- **`in_memory/event_bus.py` — unused `_TEvent` TypeVar**
  `_TEvent = TypeVar("_TEvent", bound=Event)` is defined but never referenced.
  Only `_TSpecificEvent` is used. Remove it.

- **`abcdef/__init__.py` — root package has no `__init__.py`; intent unclear**
  `abcdef` is a single-distribution framework (Pattern 2: one `pyproject.toml`,
  sub-packages imported directly). Without an `__init__.py`, the root is a
  namespace package, which works but gives no signal to callers or tooling.
  Add `abcdef/__init__.py` containing only a module docstring and
  `__all__ = []`. The empty `__all__` is the idiomatic Python signal that the
  root exports nothing; callers should import from sub-packages directly
  (`abcdef.core`, `abcdef.c`, etc.). The existing `Public API Boundaries`
  section in `abcdef/README.md` already documents this in prose.

- **`abcdef/specification/py.typed` — redundant PEP 561 marker**
  `abcdef/py.typed` already declares the entire package as typed. A second
  `py.typed` inside `specification/` is incorrect per PEP 561, which places
  the marker at the distribution root only. Remove
  `abcdef/specification/py.typed`.

- **`abcdef/README.md` — `de/` row missing from the marker table**
  The Architecture Markers table lists `c/` (`__cqrs_type__`), `d/`
  (`__ddd_type__`), and `specification/` (`__ddd_type__`), but omits `de/`
  entirely. Add a row for `de/` showing `@event_store` (and `@aggregate_store`
  if added above) mapping to `__de_type__`.

- **`d/aggregate.py` — `AggregateRoot.__init_subclass__` docstring missing
  `**kwargs`**
  `Event.__init_subclass__` documents its `**kwargs` parameter; the identical
  signature on `AggregateRoot.__init_subclass__` omits it. Add the `**kwargs`
  entry to the `Args` section for consistency.

- **`abcdef/README.md` — `Projector` position in Core Concepts implies `de/`
  association**
  In the bullet list, `Projector` appears between `EventSourcedRepository` and
  `Specification`, making it read as a `de/` concept. It lives in `c/`. Reorder
  the bullet list to group `Projector` with other `c/` concepts, or add a note
  clarifying its package.
