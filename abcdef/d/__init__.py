"""d -- DDD building blocks.

Base classes and abstractions for Domain-Driven Design concepts: aggregates, value
objects, repositories, and domain events.
"""

from .aggregate import AggregateId, AggregateRoot
from .domain_event import DomainEvent, DomainEventRegistry
from .event_emitting_aggregate import EventEmittingAggregate
from .markers import (
    aggregate,
    domain_service,
    factory,
    identifier,
    repository,
    value_object,
)
from .repository import Repository
from .value_object import ValueObject

__all__ = [
    "AggregateId",
    "AggregateRoot",
    "DomainEvent",
    "DomainEventRegistry",
    "EventEmittingAggregate",
    "Repository",
    "ValueObject",
    "aggregate",
    "domain_service",
    "factory",
    "identifier",
    "repository",
    "value_object",
]
