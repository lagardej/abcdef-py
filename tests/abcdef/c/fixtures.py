"""Shared fixtures for c/ tests."""

from abcdef.c import Command, CommandHandler, Query, QueryHandler
from abcdef.core import Result


class DummyCommand(Command):
    """Dummy command carrying a single value."""

    def __init__(self, value: str) -> None:
        """Initialise with a value."""
        self.value = value


class DummyQuery(Query):
    """Dummy query carrying a single key."""

    def __init__(self, key: str) -> None:
        """Initialise with a key."""
        self.key = key


class DummyResult(Result):
    """Dummy result carrying a string output."""

    def __init__(self, output: str) -> None:
        """Initialise with an output string."""
        self.output = output


class DummyCommandHandler(CommandHandler[DummyCommand, DummyResult]):
    """Dummy command handler for testing."""

    def handle(self, command: DummyCommand) -> DummyResult:
        """Handle the dummy command."""
        return DummyResult(output=f"Handled: {command.value}")


class DummyQueryHandler(QueryHandler[DummyQuery, DummyResult]):
    """Dummy query handler for testing."""

    def handle(self, query: DummyQuery) -> DummyResult:
        """Handle the dummy query."""
        return DummyResult(output=f"Queried: {query.key}")


__all__ = [
    "DummyCommand",
    "DummyCommandHandler",
    "DummyQuery",
    "DummyQueryHandler",
    "DummyResult",
]
