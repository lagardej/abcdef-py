"""c -- CQRS building blocks.

Base classes, marker interfaces, and bus abstractions for Command/Query Responsibility
Segregation.
"""

from .command import Command, CommandHandler
from .document import Document
from .document_store import DocumentStore
from .markers import (
    command,
    command_handler,
    document,
    document_store,
    projector,
    query,
    query_handler,
)
from .message_bus import CommandBus, EventBus, MessageBus, QueryBus
from .projector import Projector
from .query import Query, QueryHandler
from .registry import CommandRegistry, QueryRegistry

__all__ = [
    "Command",
    "CommandBus",
    "CommandHandler",
    "CommandRegistry",
    "Document",
    "DocumentStore",
    "EventBus",
    "MessageBus",
    "Projector",
    "Query",
    "QueryBus",
    "QueryHandler",
    "QueryRegistry",
    "command",
    "command_handler",
    "document",
    "document_store",
    "projector",
    "query",
    "query_handler",
]
