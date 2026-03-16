# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

(none)

---

## Tasks

(none)

---

## Improvements

**I3 — Remove or rethink `aggregate_type` requirement on `EventSourcedRepository` subclasses**

`self.aggregate_type` is only used as a fallback when no aggregate store record
exists at all (no record + events present). In normal operation, the type is
always read from the record. The per-subclass declaration creates a redundant
coupling with the aggregate class's own `aggregate_type` and is a source of
divergence bugs. Consider deriving it from the aggregate class directly, or
removing the subclass requirement and making it a constructor argument.

**I1 — Extract a shared generic `EventRegistry[T]` base class**

`DomainEventRegistry`, `EventSourcedDomainEventRegistry`, and `AggregateRegistry`
are structurally identical: each has `register(key, cls)` and `get(key)` with
the same duplicate-detection logic and error format. Extract a shared generic
base or ABC to eliminate the duplication and make the contract explicit.

**I5 — Make `EventEmittingAggregate` generic over its event type**

`_pending_events` is typed as `list[DomainEvent]` on `EventEmittingAggregate`,
but `EventSourcedAggregate` narrows both `_emit_event()` and
`_get_uncommitted_events()` to `EventSourcedDomainEvent`. This requires
`type: ignore[override]` and `type: ignore[return-value]` on the overriding
methods. Making `EventEmittingAggregate` generic over the event type would
eliminate the suppression comments.

**I7 — Consolidate or document the `__es_type__` marker attribute split**

All markers use `__cqrs_type__` or `__ddd_type__` except `@event_store`, which
uses `__es_type__`. This inconsistency is undocumented. Either consolidate all
markers under a single attribute (e.g. `__abc_type__`) or add an explicit
rationale in the marker module docstrings and the README marker table.

**I4 — Remove `_get_marker` from `abcdef/core/__init__.py` `__all__`**

`_get_marker` is private by convention (underscore prefix) but is listed in
`__all__`, making it part of the public API. Either remove it from `__all__` if
it is internal, or rename it `get_marker` if it is intentionally public.

**I6 — Add a docstring note to `InMemoryRepository.save()` about reference semantics**

`InMemoryRepository.save()` stores the aggregate object reference, not a copy.
Post-save mutations to the aggregate are reflected when `get_by_id()` is called.
This is expected for an in-memory store but should be stated in the docstring to
avoid masking bugs in tests that assume persistence is a snapshot.
