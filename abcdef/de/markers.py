"""Event Sourcing architecture markers.

Decorators that mark classes with Event Sourcing concepts: event stores and aggregate
stores. Markers are inherited by subclasses.

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


def aggregate_store[T](cls: T) -> T:
    """Mark a class as an Aggregate Store.

    An Aggregate Store tracks the current version of every aggregate and optionally
    caches state snapshots for replay optimisation. It provides optimistic concurrency
    control via expected_version checks on save.

    An aggregate store is distinct from an event store: the event store holds the
    raw event stream, whereas the aggregate store holds version records and optional
    state snapshots used to accelerate replay.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as an aggregate store.

    Returns:
        The class with __de_type__ = "aggregate_store" metadata.
    """
    cls.__de_type__ = "aggregate_store"  # type: ignore[attr-defined]
    return cls
