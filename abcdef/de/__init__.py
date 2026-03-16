"""de -- DDD + Event Sourcing intersection.

Contains concepts that belong to both DDD and Event Sourcing:
event-sourced aggregates, repositories, event stores, aggregate records,
and the EventSourcedDomainEvent hierarchy.
"""

from .aggregate_store import AggregateRecord, AggregateStore, VersionConflictError
from .event_sourced_aggregate import (
    AggregateRegistry,
    AggregateState,
    EventSourcedAggregate,
)
from .event_sourced_domain_event import (
    EventSourcedDomainEvent,
    EventSourcedDomainEventRegistry,
)
from .event_sourced_repository import EventSourcedRepository
from .event_store import EventStore
from .markers import event_store

__all__ = [
    "AggregateRecord",
    "AggregateRegistry",
    "AggregateState",
    "AggregateStore",
    "EventSourcedAggregate",
    "EventSourcedDomainEvent",
    "EventSourcedDomainEventRegistry",
    "EventSourcedRepository",
    "EventStore",
    "VersionConflictError",
    "event_store",
]
