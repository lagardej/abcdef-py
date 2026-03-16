"""Command and query registries/dispatchers."""

from collections.abc import Callable
from typing import Any, TypeVar, cast

from abcdef.core.result import Result

from .command import Command
from .message_bus import CommandBus, QueryBus
from .query import Query

_TSpecificCommand = TypeVar("_TSpecificCommand", bound=Command)
_TSpecificQuery = TypeVar("_TSpecificQuery", bound=Query)


class CommandRegistry(CommandBus):
    """Registry and dispatcher for commands.

    Maintains a mapping of command types to their handlers and dispatches
    incoming commands to the appropriate handler.
    """

    def __init__(self) -> None:
        """Initialise the command registry."""
        self._handlers: dict[type[Command], Callable[..., Any]] = {}

    def subscribe(  # type: ignore[override]
        self,
        message_type: type[_TSpecificCommand],
        handler: Callable[[_TSpecificCommand], Any],
    ) -> None:
        """Register a command handler.

        Args:
            message_type: The command type to handle.
            handler: The command handler function.

        Raises:
            ValueError: If a handler is already registered for this command type.
        """
        if message_type in self._handlers:
            raise ValueError(
                f"Handler already registered for command type {message_type.__name__}"
            )
        self._handlers[message_type] = handler

    def publish(self, message: Command) -> Result:
        """Dispatch a command to its handler.

        Args:
            message: The command to dispatch.

        Returns:
            The result returned by the handler.

        Raises:
            ValueError: If no handler is registered for this command type.
        """
        handler = self._handlers.get(type(message))
        if handler is None:
            raise ValueError(
                f"No handler registered for command type {type(message).__name__}"
            )
        return cast("Result", handler(message))


class QueryRegistry(QueryBus):
    """Registry and dispatcher for queries.

    Maintains a mapping of query types to their handlers and dispatches
    incoming queries to the appropriate handler.
    """

    def __init__(self) -> None:
        """Initialise the query registry."""
        self._handlers: dict[type[Query], Callable[..., Any]] = {}

    def subscribe(  # type: ignore[override]
        self,
        message_type: type[_TSpecificQuery],
        handler: Callable[[_TSpecificQuery], Any],
    ) -> None:
        """Register a query handler.

        Args:
            message_type: The query type to handle.
            handler: The query handler function.

        Raises:
            ValueError: If a handler is already registered for this query type.
        """
        if message_type in self._handlers:
            raise ValueError(
                f"Handler already registered for query type {message_type.__name__}"
            )
        self._handlers[message_type] = handler

    def publish(self, message: Query) -> Result:
        """Dispatch a query to its handler.

        Args:
            message: The query to dispatch.

        Returns:
            The result returned by the handler.

        Raises:
            ValueError: If no handler is registered for this query type.
        """
        handler = self._handlers.get(type(message))
        if handler is None:
            raise ValueError(
                f"No handler registered for query type {type(message).__name__}"
            )
        return cast("Result", handler(message))
