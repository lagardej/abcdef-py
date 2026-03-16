"""Shared fixtures for in_memory/ tests."""

import datetime

from abcdef.core import Event
from abcdef.d import AggregateId, AggregateRoot


class DummyAggregate(AggregateRoot):
    """Dummy aggregate for in-memory repository tests."""

    def __init__(self, aggregate_id: AggregateId, value: str = "") -> None:
        """Initialise with an aggregate_id and optional value."""
        super().__init__(aggregate_id)
        self.value = value


_TS = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)


class OrderPlaced(Event):
    """Dummy event representing an order being placed."""

    event_type = "order_placed"
    order_id: str

    def __init__(self, order_id: str) -> None:
        """Initialise with an order_id."""
        super().__init__(occurred_at=_TS)
        object.__setattr__(self, "order_id", order_id)


class OrderCancelled(Event):
    """Dummy event representing an order being cancelled."""

    event_type = "order_cancelled"
    order_id: str

    def __init__(self, order_id: str) -> None:
        """Initialise with an order_id."""
        super().__init__(occurred_at=_TS)
        object.__setattr__(self, "order_id", order_id)


__all__ = [
    "DummyAggregate",
    "OrderCancelled",
    "OrderPlaced",
]
