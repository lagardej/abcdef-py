"""CQRS architecture markers.

Decorators that mark classes with CQRS concepts: commands, queries,
handlers, documents, document stores, and projectors.
Markers are inherited by subclasses.
"""


def command[T](cls: T) -> T:
    """Mark a class as a Command.

    A Command represents an intent to perform an action that mutates state.
    Commands are processed by CommandHandlers.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a command.

    Returns:
        The class with __cqrs_type__ = "command" metadata.
    """
    cls.__cqrs_type__ = "command"  # type: ignore[attr-defined]
    return cls


def command_handler[T](cls: T) -> T:
    """Mark a class as a Command Handler.

    A CommandHandler processes a specific Command type and orchestrates
    changes to aggregates or other domain objects.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a command handler.

    Returns:
        The class with __cqrs_type__ = "command_handler" metadata.
    """
    cls.__cqrs_type__ = "command_handler"  # type: ignore[attr-defined]
    return cls


def query[T](cls: T) -> T:
    """Mark a class as a Query.

    A Query represents a request to retrieve data without mutating state.
    Queries are processed by QueryHandlers.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a query.

    Returns:
        The class with __cqrs_type__ = "query" metadata.
    """
    cls.__cqrs_type__ = "query"  # type: ignore[attr-defined]
    return cls


def query_handler[T](cls: T) -> T:
    """Mark a class as a Query Handler.

    A QueryHandler processes a specific Query type and returns a result
    by reading from document stores.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a query handler.

    Returns:
        The class with __cqrs_type__ = "query_handler" metadata.
    """
    cls.__cqrs_type__ = "query_handler"  # type: ignore[attr-defined]
    return cls


def document[T](cls: T) -> T:
    """Mark a class as a Document (query-side read model).

    A Document is a denormalised, query-optimised data container built from
    domain events. It is the unit of storage in a DocumentStore.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a document.

    Returns:
        The class with __cqrs_type__ = "document" metadata.
    """
    cls.__cqrs_type__ = "document"  # type: ignore[attr-defined]
    return cls


def document_store[T](cls: T) -> T:
    """Mark a class as a Document Store.

    A DocumentStore persists and retrieves Documents. It is the query-side
    counterpart to the Repository on the write side.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a document store.

    Returns:
        The class with __cqrs_type__ = "document_store" metadata.
    """
    cls.__cqrs_type__ = "document_store"  # type: ignore[attr-defined]
    return cls


def projector[T](cls: T) -> T:
    """Mark a class as a Projector.

    A Projector subscribes to domain events and updates Documents in a
    DocumentStore. It is the actor that performs the projection — the
    Document is the result.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a projector.

    Returns:
        The class with __cqrs_type__ = "projector" metadata.
    """
    cls.__cqrs_type__ = "projector"  # type: ignore[attr-defined]
    return cls
