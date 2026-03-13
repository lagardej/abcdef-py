"""CQRS+DDD+Event Sourcing architecture markers.

Decorators that mark classes sitting at the intersection of all three
paradigms. Currently: the event marker, since an Event is simultaneously
a CQRS message, a DDD domain concept, and the atomic unit of Event Sourcing.
"""


def event[T](cls: T) -> T:
    """Mark a class as an Event.

    An Event represents an immutable record of something that happened
    in the domain. Events are the source of truth for state changes.

    Marker is inherited by subclasses.

    Args:
        cls: The class to mark as an event.

    Returns:
        The class with __cqrs_type__ = "event" metadata.
    """
    cls.__cqrs_type__ = "event"  # type: ignore[attr-defined]
    return cls
