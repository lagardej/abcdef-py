"""de — DDD + Event Sourcing intersection.

Contains concepts that belong to both DDD and Event Sourcing:
event-sourced aggregates, repositories, event stores, and snapshots.
"""

from .aggregate_store import AggregateStore, Snapshot
from .event_sourced_aggregate import AggregateState, EventSourcedAggregate
from .event_sourced_repository import EventSourcedRepository
from .event_store import EventStore

__all__ = [
    "AggregateState",
    "AggregateStore",
    "EventSourcedAggregate",
    "EventSourcedRepository",
    "EventStore",
    "Snapshot",
]
