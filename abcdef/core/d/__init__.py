"""d — DDD building blocks.

Base classes and abstractions for Domain-Driven Design concepts:
aggregates, value objects, and repositories.
"""

from .aggregate import AggregateId, AggregateRoot
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
    "Repository",
    "ValueObject",
    "aggregate",
    "domain_service",
    "factory",
    "identifier",
    "repository",
    "value_object",
]
