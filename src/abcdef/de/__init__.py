"""Event-sourced extensions that build on the DDD model from abcdef.d."""

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
from .markers import aggregate_store, event_store

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
    "aggregate_store",
    "event_store",
]
