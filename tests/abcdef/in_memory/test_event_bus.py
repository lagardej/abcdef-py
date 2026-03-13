"""Tests for InMemoryEventBus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from abcdef.in_memory import InMemoryEventBus
from tests.abcdef.in_memory.fixtures import OrderCancelled, OrderPlaced

if TYPE_CHECKING:
    from abcdef.core import Event


class TestInMemoryEventBus:
    """Tests for InMemoryEventBus."""

    def test_published_event_reaches_subscriber(self) -> None:
        """A subscribed handler is called when its event type is published."""
        bus = InMemoryEventBus()
        received: list[OrderPlaced] = []
        bus.subscribe(OrderPlaced, received.append)

        bus.publish(OrderPlaced("order-1"))

        assert len(received) == 1
        assert received[0].order_id == "order-1"

    def test_multiple_subscribers_all_called(self) -> None:
        """All handlers subscribed to an event type are called in order."""
        bus = InMemoryEventBus()
        log: list[str] = []
        bus.subscribe(OrderPlaced, lambda e: log.append("handler-a"))
        bus.subscribe(OrderPlaced, lambda e: log.append("handler-b"))

        bus.publish(OrderPlaced("order-1"))

        assert log == ["handler-a", "handler-b"]

    def test_unsubscribed_event_is_silently_ignored(self) -> None:
        """Publishing an event with no subscribers does not raise."""
        bus = InMemoryEventBus()
        bus.publish(OrderPlaced("order-1"))

    def test_handler_only_called_for_its_event_type(self) -> None:
        """A handler subscribed to one event type is not called for other types."""
        bus = InMemoryEventBus()
        received: list[Event] = []
        bus.subscribe(OrderPlaced, received.append)

        bus.publish(OrderCancelled("order-1"))

        assert received == []

    def test_multiple_event_types_routed_independently(self) -> None:
        """Handlers for different event types are called independently and correctly."""
        bus = InMemoryEventBus()
        placed: list[OrderPlaced] = []
        cancelled: list[OrderCancelled] = []
        bus.subscribe(OrderPlaced, placed.append)
        bus.subscribe(OrderCancelled, cancelled.append)

        bus.publish(OrderPlaced("order-1"))
        bus.publish(OrderCancelled("order-2"))

        assert len(placed) == 1
        assert placed[0].order_id == "order-1"
        assert len(cancelled) == 1
        assert cancelled[0].order_id == "order-2"

    def test_same_handler_can_subscribe_to_multiple_event_types(self) -> None:
        """A single handler can be subscribed to multiple event types."""
        bus = InMemoryEventBus()
        received: list[Event] = []
        bus.subscribe(OrderPlaced, received.append)
        bus.subscribe(OrderCancelled, received.append)

        bus.publish(OrderPlaced("order-1"))
        bus.publish(OrderCancelled("order-2"))

        assert len(received) == 2

    def test_publish_multiple_events_accumulates_calls(self) -> None:
        """Publishing the same event type multiple times calls the handler each time."""
        bus = InMemoryEventBus()
        received: list[OrderPlaced] = []
        bus.subscribe(OrderPlaced, received.append)

        bus.publish(OrderPlaced("order-1"))
        bus.publish(OrderPlaced("order-2"))

        assert len(received) == 2
        assert received[0].order_id == "order-1"
        assert received[1].order_id == "order-2"

    def test_handlers_called_in_subscription_order(self) -> None:
        """Handlers are invoked in the order they were subscribed."""
        bus = InMemoryEventBus()
        log: list[int] = []
        bus.subscribe(OrderPlaced, lambda e: log.append(1))
        bus.subscribe(OrderPlaced, lambda e: log.append(2))
        bus.subscribe(OrderPlaced, lambda e: log.append(3))

        bus.publish(OrderPlaced("order-1"))

        assert log == [1, 2, 3]
