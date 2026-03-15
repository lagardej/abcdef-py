"""DomainEvent -- an Event raised by a specific aggregate instance."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .event import Event

if TYPE_CHECKING:
    import datetime


class DomainEventRegistry:
    """Registry of DomainEvent subclasses keyed by event_type.

    A plain, injectable class with no global state. Callers create an
    instance and register event classes into it explicitly.
    """

    def __init__(self) -> None:
        """Initialise with an empty registry."""
        self._registry: dict[str, type[DomainEvent]] = {}

    def register(self, event_type: str, cls: type[DomainEvent]) -> None:
        """Register a concrete DomainEvent subclass under its event_type.

        Args:
            event_type: The stable string identifier for the class.
            cls: The concrete DomainEvent subclass to register.

        Raises:
            TypeError: If the event_type is already registered.
        """
        if event_type in self._registry:
            raise TypeError(
                f"event_type '{event_type}' is already registered "
                f"by {self._registry[event_type].__qualname__}. "
                f"Each event_type must be unique."
            )
        self._registry[event_type] = cls

    def get(self, event_type: str) -> type[DomainEvent]:
        """Look up a registered DomainEvent subclass by event_type.

        Args:
            event_type: The stable string identifier for the class.

        Returns:
            The concrete subclass registered under that name.

        Raises:
            KeyError: If no class is registered for the given event_type.
        """
        return self._registry[event_type]


class DomainEvent(Event):
    """An Event raised by an event-sourced domain aggregate.

    Extends Event with the identity of the aggregate instance that raised
    it. ``aggregate_id`` is scoped to a single aggregate type: it
    identifies *which instance* of that aggregate emitted the event.
    Uniqueness across different aggregate types is not guaranteed.

    Concrete subclasses must declare a non-empty ``event_type`` class
    variable. The event_type check is enforced by Event.__init_subclass__.

    Args:
        occurred_at: When the event occurred.
        aggregate_id: String identity of the aggregate instance that
            raised this event, within its aggregate type.
    """

    _abstract_event = True
    aggregate_id: str

    def __init__(self, *, occurred_at: datetime.datetime, aggregate_id: str) -> None:
        """Initialise the domain event.

        Args:
            occurred_at: The timestamp at which this event occurred.
            aggregate_id: The identity of the aggregate instance that
                raised this event.
        """
        super().__init__(occurred_at=occurred_at)
        object.__setattr__(self, "aggregate_id", aggregate_id)
