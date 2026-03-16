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

**I6 — Add a docstring note to `InMemoryRepository.save()` about reference semantics**

`InMemoryRepository.save()` stores the aggregate object reference, not a copy.
Post-save mutations to the aggregate are reflected when `get_by_id()` is called.
This is expected for an in-memory store but should be stated in the docstring to
avoid masking bugs in tests that assume persistence is a snapshot.
