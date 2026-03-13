"""Shared fixtures for in_memory/ tests."""

from abcdef.core import AggregateId, AggregateRoot, Event


class DummyAggregate(AggregateRoot):
    """Dummy aggregate for in-memory repository tests."""

    def __init__(self, aggregate_id: AggregateId, value: str = "") -> None:
        """Initialise with an aggregate_id and optional value."""
        super().__init__(aggregate_id)
        self.value = value


class OrderPlaced(Event):
    """Dummy event representing an order being placed."""

    def __init__(self, order_id: str) -> None:
        """Initialise with an order_id."""
        self.order_id = order_id


class OrderCancelled(Event):
    """Dummy event representing an order being cancelled."""

    def __init__(self, order_id: str) -> None:
        """Initialise with an order_id."""
        self.order_id = order_id


__all__ = [
    "DummyAggregate",
    "OrderCancelled",
    "OrderPlaced",
]
