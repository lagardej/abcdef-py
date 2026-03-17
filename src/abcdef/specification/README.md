# `abcdef.specification`

Composable business-rule predicates using the Specification pattern.

## Purpose

`abcdef.specification` provides a small, focused abstraction for expressing
reusable business rules as composable predicates. Specifications can be
combined with `&`, `|`, and `~` and applied where rule composition matters.

This package is intentionally small and independent. It can support domain
models, but it does not depend on the rest of the framework.

## Internal Dependencies

`abcdef.specification` has no dependency on other `abcdef` subpackages.

## Public Imports

Import from the package facade, for example
`from abcdef.specification import Specification`.

Public exports include:

- `Specification`
- `specification`

## Key Concepts

- `Specification` — abstract predicate for business rules
- `&` — conjunction of two specifications
- `|` — disjunction of two specifications
- `~` — negation of a specification
- `@specification` — runtime architecture marker

## Use When

- you want reusable and testable rule objects
- business rules need to be composed declaratively
- a domain model benefits from explicit predicate semantics

## Do Not Use For

- workflow orchestration or application services
- aggregates, repositories, or event-storage concerns
- replacing simple inline checks where no reuse is needed

## See Also

- [Package reference](../README.md)
- [`abcdef.d`](../d/README.md)

