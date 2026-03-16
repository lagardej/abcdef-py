# Backlog

Short-lived items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Tasks


**T3 — Fix `abcdef/core/__init__.py` module docstring**

The docstring claims `d/` "includes Event, DomainEvent, EventEmittingAggregate"
which is factually correct, but the framing originates from the defunct `cde/`
split in the README. Once T2 is resolved, update the docstring to remove any
reference to `cde/`.

**T4 — Reformat all docstrings and comments to the 72-character line limit**

AGENTS.md specifies 72 characters maximum for docstrings and comments (PEP 8
convention), distinct from the 88-character limit enforced by ruff for code.
This limit is not enforced by tooling and has drifted across the codebase.
Pass over every file in `abcdef/` and `tests/abcdef/` and reformat all
docstring and comment lines that exceed 72 characters. Wrap continuation
lines at the same indentation level as the opening text.

---

## Improvements

**I1 — Extract a shared generic `EventRegistry[T]` base class**

`DomainEventRegistry`, `EventSourcedDomainEventRegistry`, and `AggregateRegistry`
are structurally identical: each has `register(key, cls)` and `get(key)` with
the same duplicate-detection logic and error format. Extract a shared generic
base or ABC to eliminate the duplication and make the contract explicit.

**I2 — `AggregateRoot.__eq__` — replace `isinstance` check with `type()` equality**

The current check `isinstance(other, self.__class__)` is asymmetric: a subclass
instance passes against its parent, but the parent does not pass against the
subclass. Replace with `type(self) is type(other)` for consistent, symmetric
behaviour.

**I3 — Remove or rethink `aggregate_type` requirement on `EventSourcedRepository` subclasses**

`self.aggregate_type` is only used as a fallback when no aggregate store record
exists at all (no record + events present). In normal operation, the type is
always read from the record. The per-subclass declaration creates a redundant
coupling with the aggregate class's own `aggregate_type` and is a source of
divergence bugs. Consider deriving it from the aggregate class directly, or
removing the subclass requirement and making it a constructor argument.

**I4 — Remove `_get_marker` from `abcdef/core/__init__.py` `__all__`**

`_get_marker` is private by convention (underscore prefix) but is listed in
`__all__`, making it part of the public API. Either remove it from `__all__` if
it is internal, or rename it `get_marker` if it is intentionally public.

**I5 — Make `EventEmittingAggregate` generic over its event type**

`_pending_events` is typed as `list[DomainEvent]` on `EventEmittingAggregate`,
but `EventSourcedAggregate` narrows both `_emit_event()` and
`_get_uncommitted_events()` to `EventSourcedDomainEvent`. This requires
`type: ignore[override]` and `type: ignore[return-value]` on the overriding
methods. Making `EventEmittingAggregate` generic over the event type would
eliminate the suppression comments.

**I6 — Add a docstring note to `InMemoryRepository.save()` about reference semantics**

`InMemoryRepository.save()` stores the aggregate object reference, not a copy.
Post-save mutations to the aggregate are reflected when `get_by_id()` is called.
This is expected for an in-memory store but should be stated in the docstring to
avoid masking bugs in tests that assume persistence is a snapshot.

**I7 — Consolidate or document the `__es_type__` marker attribute split**

All markers use `__cqrs_type__` or `__ddd_type__` except `@event_store`, which
uses `__es_type__`. This inconsistency is undocumented. Either consolidate all
markers under a single attribute (e.g. `__abc_type__`) or add an explicit
rationale in the marker module docstrings and the README marker table.
