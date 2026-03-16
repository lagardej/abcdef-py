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

**I4 — Remove `_get_marker` from `abcdef/core/__init__.py` `__all__`**

`_get_marker` is private by convention (underscore prefix) but is listed in
`__all__`, making it part of the public API. Either remove it from `__all__` if
it is internal, or rename it `get_marker` if it is intentionally public.

**I6 — Add a docstring note to `InMemoryRepository.save()` about reference semantics**

`InMemoryRepository.save()` stores the aggregate object reference, not a copy.
Post-save mutations to the aggregate are reflected when `get_by_id()` is called.
This is expected for an in-memory store but should be stated in the docstring to
avoid masking bugs in tests that assume persistence is a snapshot.
