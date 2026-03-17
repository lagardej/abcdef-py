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

- **`d/aggregate.py` — `AggregateRoot.__init_subclass__` docstring missing
  `**kwargs`**
  `Event.__init_subclass__` documents its `**kwargs` parameter; the identical
  signature on `AggregateRoot.__init_subclass__` omits it. Add the `**kwargs`
  entry to the `Args` section for consistency.
