"""c — CQRS building blocks.

Base classes, marker interfaces, and bus abstractions for
Command/Query Responsibility Segregation.
"""

from .command import Command, CommandHandler, TCommand, TResult
from .markers import (
    command,
    command_handler,
    projection,
    query,
    query_handler,
)
from .message_bus import CommandBus, EventBus, MessageBus, QueryBus
from .query import Query, QueryHandler, TQuery, TQueryResult
from .registry import CommandRegistry, QueryRegistry
from .result import Result

__all__ = [
    "Command",
    "CommandBus",
    "CommandHandler",
    "CommandRegistry",
    "EventBus",
    "MessageBus",
    "Query",
    "QueryBus",
    "QueryHandler",
    "QueryRegistry",
    "Result",
    "TCommand",
    "TQuery",
    "TQueryResult",
    "TResult",
    "command",
    "command_handler",
    "projection",
    "query",
    "query_handler",
]
