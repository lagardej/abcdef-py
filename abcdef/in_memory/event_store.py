"""In-memory implementation of EventStore."""

from collections.abc import Sequence

from abcdef.d import AggregateId, AggregateRoot
from abcdef.de import EventSourcedDomainEvent, EventStore


class InMemoryEventStore[TId: AggregateId, TEntity: AggregateRoot](
    EventStore[TId, TEntity]
):
    """In-memory EventStore implementation.

    Stores events in a plain dict keyed by string representation of the
    aggregate ID. Suitable for testing and lightweight use cases where
    persistence is not required.

    Append order across all aggregates is preserved in a separate list,
    supporting projections that consume all events in order.
    """

    def __init__(self) -> None:
        """Initialise the event store with empty storage."""
        self._store: dict[str, list[EventSourcedDomainEvent]] = {}
        self._all: list[EventSourcedDomainEvent] = []

    def append_events(
        self, aggregate_id: TId, events: Sequence[EventSourcedDomainEvent]
    ) -> None:
        """Append events for an aggregate to the store.

        Args:
            aggregate_id: The ID of the aggregate emitting events.
            events: Sequence of domain events to store.
        """
        key = str(aggregate_id)
        if key not in self._store:
            self._store[key] = []
        self._store[key].extend(events)
        self._all.extend(events)

    def get_events(
        self, aggregate_id: TId, after_version: int | None = None
    ) -> list[EventSourcedDomainEvent]:
        """Retrieve events for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.
            after_version: If provided, only events from this position
                onwards are returned. ``after_version=N`` skips the
                first N events (exclusive lower bound). If None, all
                events are returned.

        Returns:
            A copy of the matching events in chronological order.
        """
        events = self._store.get(str(aggregate_id), [])
        if after_version is not None:
            return events[after_version:].copy()
        return events.copy()

    def get_all_events(self) -> list[EventSourcedDomainEvent]:
        """Retrieve all events across all aggregates in append order.

        Returns:
            A copy of all stored events in chronological order.
        """
        return self._all.copy()
