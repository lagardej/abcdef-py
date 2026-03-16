# Backlog

Short-listed items: bugs, improvements, and refactoring tasks. Resolved entries are removed.

---

## Bugs

(none)

---

## Tasks

(none)

---

## Improvements

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
