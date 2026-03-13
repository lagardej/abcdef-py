"""Marker interface for domain events."""

from . import markers


@markers.event
class Event:
    """Marker interface for events.

    An Event represents an immutable record of something that happened in the domain.
    Events are published after commands are executed and are the source of truth
    for domain state changes.
    """

    pass
