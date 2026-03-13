"""In-memory implementation of EventStore."""

from abcdef.core import AggregateId, AggregateRoot, EventStore


class InMemoryEventStore[TId: AggregateId, TEntity: AggregateRoot](
    EventStore[TId, TEntity]
):
    """In-memory EventStore implementation.

    Stores events in a plain dict keyed by string representation of the
    aggregate ID's UUID. Suitable for testing and lightweight use cases
    where persistence is not required.

    Append order across all aggregates is preserved in a separate list,
    supporting projections that consume all events in order.
    """

    def __init__(self) -> None:
        """Initialise the event store with empty storage."""
        self._store: dict[str, list] = {}
        self._all: list = []

    def append_events(self, aggregate_id: TId, events: list) -> None:
        """Append events for an aggregate to the store.

        Args:
            aggregate_id: The ID of the aggregate emitting events.
            events: List of domain events to store.
        """
        key = str(aggregate_id.value)
        if key not in self._store:
            self._store[key] = []
        self._store[key].extend(events)
        self._all.extend(events)

    def get_events(self, aggregate_id: TId, from_version: int | None = None) -> list:
        """Retrieve events for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.
            from_version: If provided, only events at this version index and
                later are returned. If None, all events are returned.

        Returns:
            A copy of the matching events in chronological order.
        """
        events = self._store.get(str(aggregate_id.value), [])
        if from_version is not None:
            return events[from_version:].copy()
        return events.copy()

    def get_all_events(self) -> list:
        """Retrieve all events across all aggregates in append order.

        Returns:
            A copy of all stored events in chronological order.
        """
        return self._all.copy()
