"""Event Store abstraction for event sourcing."""

from abc import ABC, abstractmethod

from ..d import AggregateId, AggregateRoot
from ..d import markers as d_markers


@d_markers.repository
class EventStore[TId: AggregateId, TEntity: AggregateRoot](ABC):
    """Base interface for event stores.

    An EventStore is the single source of truth in event sourcing.
    It stores all domain events in append-only fashion (immutable).

    Aggregates are reconstructed by replaying events from the event store.

    Responsibilities:
    - Store events immutably (append-only)
    - Retrieve event history for an aggregate
    - Support event snapshots for performance optimisation
    """

    @abstractmethod
    def append_events(self, aggregate_id: TId, events: list) -> None:
        """Append events for an aggregate to the store.

        Events are immutable once stored. This method should be atomic.

        Args:
            aggregate_id: The ID of the aggregate emitting events.
            events: List of domain events to store.
        """
        pass

    @abstractmethod
    def get_events(self, aggregate_id: TId, from_version: int | None = None) -> list:
        """Retrieve events for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.
            from_version: If provided, only events at this version index and
                later are returned. Equivalent to skipping the first
                ``from_version`` events. If None, all events are returned.

        Returns:
            List of events in chronological order.
        """
        pass

    @abstractmethod
    def get_all_events(self) -> list:
        """Retrieve all events from the store (for projections).

        Returns:
            List of all events in chronological order.
        """
        pass
