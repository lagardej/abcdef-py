"""Event Store abstraction for event sourcing."""

from abc import ABC, abstractmethod
from collections.abc import Sequence

from ..d import AggregateId, AggregateRoot
from . import markers as de_markers
from .event_sourced_domain_event import EventSourcedDomainEvent


@de_markers.event_store
class EventStore[TId: AggregateId, TEntity: AggregateRoot](ABC):
    """Base interface for event stores.

    An EventStore is the single source of truth in event sourcing. It stores all domain
    events in append-only fashion (immutable).

    Aggregates are reconstructed by replaying events from the event store.

    Responsibilities:
    - Store events immutably (append-only)
    - Retrieve event history for an aggregate
    - Support event snapshots for performance optimisation

    Ordering contract: implementations must preserve append order per aggregate.
    get_events() returns events in chronological (append) order. get_all_events()
    returns events across all aggregates in global append order. Persistent backends
    must honour this contract explicitly.
    """

    @abstractmethod
    def append_events(
        self,
        aggregate_id: TId,
        events: Sequence[EventSourcedDomainEvent],
    ) -> None:
        """Append events for an aggregate to the store.

        Events are immutable once stored. This method should be atomic.

        Args:
            aggregate_id: The ID of the aggregate emitting events.
            events: Sequence of domain events to store.
        """
        pass

    @abstractmethod
    def get_events(
        self, aggregate_id: TId, after_version: int | None = None
    ) -> list[EventSourcedDomainEvent]:
        """Retrieve events for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.
            after_version: If provided, only events from this position onwards are
                returned. The value is treated as an exclusive lower bound:
                ``after_version=N`` skips the first N events and returns the rest,
                i.e. the event at list index N is the first one included.
                Example: 3 events stored (indices 0, 1, 2); ``after_version=2``
                returns only the third event. ``after_version=0`` returns all events.
                If None, all events are returned.

        Returns:
            List of events in chronological order.
        """
        pass

    @abstractmethod
    def get_all_events(self) -> list[EventSourcedDomainEvent]:
        """Retrieve all events from the store (for projections).

        Returns events across all aggregates in global append order.

        Returns:
            List of all events in chronological order.
        """
        pass
