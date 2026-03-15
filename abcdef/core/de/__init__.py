"""de -- DDD + Event Sourcing intersection.

Contains concepts that belong to both DDD and Event Sourcing:
event-sourced aggregates, repositories, event stores, aggregate records,
and the event hierarchy (Event, DomainEvent).
"""

from .aggregate_store import AggregateRecord, AggregateStore, VersionConflictError
from .domain_event import DomainEvent
from .event import Event
from .event_sourced_aggregate import AggregateState, EventSourcedAggregate
from .event_sourced_repository import EventSourcedRepository
from .event_store import EventStore
from .markers import event_store

__all__ = [
    "AggregateRecord",
    "AggregateState",
    "AggregateStore",
    "DomainEvent",
    "Event",
    "EventSourcedAggregate",
    "EventSourcedRepository",
    "EventStore",
    "VersionConflictError",
    "event_store",
]
