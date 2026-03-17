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

- **`abcdef/README.md` — `in_memory/` has no row in the Core Concepts table**
  Every other package in the Structure block has a table entry; `in_memory/` does not.
  Either add a row (listing `InMemoryEventStore`, `InMemoryAggregateStore`, etc.) or
  add a note explaining the omission is intentional (implementations, not concepts).

- **`abcdef/README.md` — Class Hierarchies section has no tree for supporting `d/`
  types**
  `AggregateId` and `ValueObject` have no hierarchy shown. Neither fits the message or
  aggregate trees. Consider a short "Value types" or "Identity" subsection, or a note
  that these are standalone base classes with no subclass tree in the framework.
