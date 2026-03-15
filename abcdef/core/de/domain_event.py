"""DomainEvent -- an Event raised by a specific aggregate instance."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    import datetime


class DomainEvent(Event):
    """An Event raised by an event-sourced domain aggregate.

    Extends Event with the identity of the aggregate instance that raised it.
    ``aggregate_id`` is scoped to a single aggregate type: it identifies
    *which instance* of that aggregate emitted the event. Uniqueness across
    different aggregate types is not guaranteed.

    Concrete subclasses must declare a non-empty ``event_type`` class variable.

    Args:
        occurred_at: When the event occurred.
        aggregate_id: String identity of the aggregate instance that raised
            this event, within its aggregate type.
    """

    _abstract_event = True

    def __init__(self, *, occurred_at: datetime.datetime, aggregate_id: str) -> None:
        """Initialise the domain event.

        Args:
            occurred_at: The timestamp at which this event occurred.
            aggregate_id: The identity of the aggregate instance that raised
                this event.
        """
        super().__init__(occurred_at=occurred_at)
        self.aggregate_id = aggregate_id
