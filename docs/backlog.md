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

- **`abcdef/README.md` — `AggregateStore` definition understates its responsibilities**
  The bullet says "Persists aggregate state records for replay optimisation" but omits
  that `AggregateStore` is also the enforcement point for optimistic concurrency control
  via `expected_version` / `VersionConflictError`. Update the definition to cover both
  responsibilities.

- **`abcdef/README.md` — `specification/` Paradigms column incorrectly says `DDD`**
  `specification/` has no dependency on DDD and uses its own `__specification_type__`
  marker precisely to reflect that independence. The Paradigms column should not say
  `DDD`. Change to `—` or a neutral label such as `Logic`.

- **`abcdef/README.md` — preamble never mentions `b/`**
  The preamble explains every other package but skips `b/`, which is the foundation
  everything else builds on. Add a sentence describing `b/` and its role.

- **`README.md` (TIC root) — no mention of `abcdef`**
  A reader of the project README would not know that `abcdef` exists as an embedded
  framework. Add a brief note under Development or Purpose describing it.

- **`AGENTS.md` — Coding Conventions: "Dataclasses for value objects and events" is
  partially inaccurate**
  `ValueObject` uses `@dataclass(frozen=True)`, correct. `Event` does not — it uses
  manual `__setattr__` / `__delattr__` enforcement. The convention as stated implies
  both use dataclasses. Clarify or qualify the statement.

- **`AGENTS.md` — Workflow step 4 ("Write the tests") applies only to code tasks**
  For documentation-only tasks the step is inapplicable and can confuse agents. Add a
  conditional note: "skip if the task produces no code".

- **`AGENTS.md` — Architecture section mixes TIC layer names with abcdef concepts**
  The layer dependency diagram and "ZERO external dependencies" rule reference
  `domain/` and `application/`, which are TIC application layer names, not abcdef
  package names. A new agent reading both READMEs may conflate the two. Add a
  clarifying note or label the section explicitly as TIC-specific.

- **`abcdef/README.md` — `abcdef.markers` not listed in Public API Boundaries**
  The Public API Boundaries section lists sub-packages only. `abcdef.markers` lives at
  the package root and is the only entry point for `_get_marker`. Add it explicitly.

- **`abcdef/README.md` — `in_memory/` has no row in the Core Concepts table**
  Every other package in the Structure block has a table entry; `in_memory/` does not.
  Either add a row (listing `InMemoryEventStore`, `InMemoryAggregateStore`, etc.) or
  add a note explaining the omission is intentional (implementations, not concepts).

- **`abcdef/README.md` — Class Hierarchies section has no tree for supporting `d/`
  types**
  `AggregateId` and `ValueObject` have no hierarchy shown. Neither fits the message or
  aggregate trees. Consider a short "Value types" or "Identity" subsection, or a note
  that these are standalone base classes with no subclass tree in the framework.
