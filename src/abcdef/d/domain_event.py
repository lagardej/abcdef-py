"""DomainEvent -- an Event raised by an event-emitting aggregate."""

from __future__ import annotations

from abcdef.b.event import Event
from abcdef.b.registry import ClassRegistry


class DomainEventRegistry(ClassRegistry["type[DomainEvent]"]):
    """Registry of DomainEvent subclasses keyed by event_type.

    A plain, injectable class with no global state. Callers create an instance and
    register event classes into it explicitly.
    """


class DomainEvent(Event):
    """An Event raised by a domain aggregate.

    Extends Event to mark events emitted by aggregates that raise events for the bus,
    regardless of whether they use event sourcing.

    Concrete subclasses must declare a non-empty ``event_type`` class variable. The
    event_type check is enforced by Event.__init_subclass__.
    """

    _abstract_event = True
