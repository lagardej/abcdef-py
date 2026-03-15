"""de -- DDD + Event Sourcing intersection.

Contains concepts that belong to both DDD and Event Sourcing:
event-sourced aggregates, repositories, event stores, aggregate records,
and the event hierarchy (Event, DomainEvent).
"""

from .aggregate_store import AggregateRecord, AggregateStore, VersionConflictError
from .domain_event import DomainEvent, DomainEventRegistry
from .event import Event
from .event_sourced_aggregate import (
    AggregateRegistry,
    AggregateState,
    EventSourcedAggregate,
)
from .event_sourced_repository import EventSourcedRepository
from .event_store import EventStore
from .markers import event_store

__all__ = [
    "AggregateRecord",
    "AggregateRegistry",
    "AggregateState",
    "AggregateStore",
    "DomainEvent",
    "DomainEventRegistry",
    "Event",
    "EventSourcedAggregate",
    "EventSourcedRepository",
    "EventStore",
    "VersionConflictError",
    "event_store",
]
