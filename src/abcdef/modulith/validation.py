"""Data structures and utilities for module discovery and validation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Violation:
    """A single modulith constraint violation.

    Attributes:
        module_name: Logical module name where violation occurred.
        violation_type: Category of violation (e.g., "read_write_constraint",
            "import_boundary", "facade_rule").
        message: Human-readable description of the violation.
        location: File path or module location where violation was found,
            relative to project root.
    """

    module_name: str
    violation_type: str
    message: str
    location: str | None = None


@dataclass(frozen=True)
class PublicApiSymbol:
    """A single symbol in a module's public API.

    Attributes:
        name: The symbol name as imported/exported.
        kind: Category of symbol — "command", "query", "event", "spi", or other.
        full_path: The fully qualified name for location/reference (e.g.,
            "myapp.orders.commands.CreateOrder").
    """

    name: str
    kind: str
    full_path: str


@dataclass(frozen=True)
class PublicApi:
    """Discovered public API of a module.

    Attributes:
        symbols: All public symbols exported at the module root.
        commands: Symbols marked as commands (`__cqrs_type__ = "command"`).
        queries: Symbols marked as queries (`__cqrs_type__ = "query"`).
        events: Symbols marked as domain events (`__ddd_type__ = "domain_event"`).
        spis: Symbols marked as SPIs (`__modulith_type__ = "spi"`).
    """

    symbols: frozenset[PublicApiSymbol]
    commands: frozenset[PublicApiSymbol]
    queries: frozenset[PublicApiSymbol]
    events: frozenset[PublicApiSymbol]
    spis: frozenset[PublicApiSymbol]

    @staticmethod
    def empty() -> PublicApi:
        """Return an empty PublicApi."""
        return PublicApi(
            symbols=frozenset(),
            commands=frozenset(),
            queries=frozenset(),
            events=frozenset(),
            spis=frozenset(),
        )
