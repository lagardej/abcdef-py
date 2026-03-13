"""CQRS architecture markers.

Decorators that mark classes with CQRS concepts: commands, queries,
handlers, and projections. Markers are inherited by subclasses.
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
    by reading from projections (read models).

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a query handler.

    Returns:
        The class with __cqrs_type__ = "query_handler" metadata.
    """
    cls.__cqrs_type__ = "query_handler"  # type: ignore[attr-defined]
    return cls


def projection[T](cls: T) -> T:
    """Mark a class as a Projection (Read Model).

    A Projection is a denormalised, optimised view of the domain state,
    built from events. Used for querying.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as a projection.

    Returns:
        The class with __cqrs_type__ = "projection" metadata.
    """
    cls.__cqrs_type__ = "projection"  # type: ignore[attr-defined]
    return cls
