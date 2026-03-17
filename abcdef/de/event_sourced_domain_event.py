"""EventSourcedDomainEvent -- a DomainEvent tied to an aggregate instance."""

from __future__ import annotations

from typing import TYPE_CHECKING

from abcdef.b.registry import ClassRegistry

from ..d.domain_event import DomainEvent

if TYPE_CHECKING:
    import datetime


class EventSourcedDomainEventRegistry(ClassRegistry["type[EventSourcedDomainEvent]"]):
    """Registry of EventSourcedDomainEvent subclasses keyed by event_type.

    A plain, injectable class with no global state. Callers create an instance and
    register event classes into it explicitly.
    """


class EventSourcedDomainEvent(DomainEvent):
    """A DomainEvent raised by an event-sourced aggregate instance.

    Extends DomainEvent with the identity of the aggregate instance that raised it.
    ``aggregate_id`` is scoped to a single aggregate type: it identifies *which
    instance* of that aggregate emitted the event. Uniqueness across different aggregate
    types is not guaranteed.

    Concrete subclasses must declare a non-empty ``event_type`` class variable. The
    event_type check is enforced by Event.__init_subclass__.

    Args:
        occurred_at: When the event occurred.
        aggregate_id: String identity of the aggregate instance that raised this event,
            within its aggregate type.
    """

    _abstract_event = True
    aggregate_id: str

    def __init__(self, *, occurred_at: datetime.datetime, aggregate_id: str) -> None:
        """Initialise the event-sourced domain event.

        Args:
            occurred_at: The timestamp at which this event occurred.
            aggregate_id: The identity of the aggregate instance that raised this event.
        """
        super().__init__(occurred_at=occurred_at)
        object.__setattr__(self, "aggregate_id", aggregate_id)
