"""de -- DDD + Event Sourcing intersection.

Contains concepts that belong to both DDD and Event Sourcing:
event-sourced aggregates, repositories, event stores, and aggregate records.
"""

from .aggregate_store import AggregateRecord, AggregateStore
from .event_sourced_aggregate import AggregateState, EventSourcedAggregate
from .event_sourced_repository import EventSourcedRepository
from .event_store import EventStore
from .markers import event_store

__all__ = [
    "AggregateRecord",
    "AggregateState",
    "AggregateStore",
    "EventSourcedAggregate",
    "EventSourcedRepository",
    "EventStore",
    "event_store",
]
