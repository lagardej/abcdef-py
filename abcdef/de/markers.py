"""Event Sourcing architecture markers.

Decorators that mark classes with Event Sourcing concepts: event stores. Markers are
inherited by subclasses.

Marker attribute convention:
- c/  uses ``__cqrs_type__``
- d/  uses ``__ddd_type__``
- de/ uses ``__de_type__``
"""


def event_store[T](cls: T) -> T:
    """Mark a class as an Event Store.

    An Event Store is the append-only persistence mechanism for domain events in an
    event-sourced system. It is the single source of truth: aggregates are reconstructed
    by replaying events retrieved from it.

    An event store is distinct from a DDD repository: a repository abstracts
    collection-like persistence of aggregates, whereas an event store provides raw event
    streams. The two concepts are not interchangeable.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as an event store.

    Returns:
        The class with __de_type__ = "event_store" metadata.
    """
    cls.__de_type__ = "event_store"  # type: ignore[attr-defined]
    return cls
