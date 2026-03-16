"""Tests for EventSourcedDomainEvent and EventSourcedDomainEventRegistry."""

from __future__ import annotations

import datetime

import pytest

from abcdef.d import Event
from abcdef.de import EventSourcedDomainEvent, EventSourcedDomainEventRegistry

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TS = datetime.datetime(2024, 1, 1, 12, 0, 0, tzinfo=datetime.UTC)


class ConcreteEventSourcedDomainEvent(EventSourcedDomainEvent):
    """Minimal concrete EventSourcedDomainEvent for testing."""

    event_type = "concrete_es_domain_event"

    def __init__(self, aggregate_id: str) -> None:
        """Initialise."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)


# ---------------------------------------------------------------------------
# EventSourcedDomainEvent
# ---------------------------------------------------------------------------


class TestEventSourcedDomainEvent:
    """Tests for EventSourcedDomainEvent."""

    def test_is_event(self) -> None:
        """EventSourcedDomainEvent is a subtype of Event."""
        assert isinstance(ConcreteEventSourcedDomainEvent("x"), Event)

    def test_aggregate_id_is_stored(self) -> None:
        """aggregate_id is accessible on the instance."""
        event = ConcreteEventSourcedDomainEvent(aggregate_id="agg-42")
        assert event.aggregate_id == "agg-42"

    def test_occurred_at_is_stored(self) -> None:
        """occurred_at is inherited and accessible."""
        assert ConcreteEventSourcedDomainEvent(aggregate_id="x").occurred_at == _TS

    def test_missing_event_type_raises(self) -> None:
        """Concrete subclass without event_type raises TypeError."""
        with pytest.raises(TypeError, match="event_type"):

            class BadEvent(EventSourcedDomainEvent):
                def __init__(self) -> None:
                    super().__init__(occurred_at=_TS, aggregate_id="x")

    def test_aggregate_id_is_immutable(self) -> None:
        """Assigning to aggregate_id after construction raises."""
        event = ConcreteEventSourcedDomainEvent(aggregate_id="agg-1")
        with pytest.raises(AttributeError):
            event.aggregate_id = "agg-2"  # type: ignore[misc]

    def test_aggregate_id_cannot_be_deleted(self) -> None:
        """Deleting aggregate_id after construction raises AttributeError."""
        event = ConcreteEventSourcedDomainEvent(aggregate_id="agg-1")
        with pytest.raises(AttributeError):
            del event.aggregate_id  # type: ignore[misc]

    def test_occurred_at_is_immutable(self) -> None:
        """Assigning to occurred_at after construction raises AttributeError."""
        event = ConcreteEventSourcedDomainEvent(aggregate_id="x")
        with pytest.raises(AttributeError):
            event.occurred_at = _TS  # type: ignore[misc]


# ---------------------------------------------------------------------------
# EventSourcedDomainEventRegistry
# ---------------------------------------------------------------------------


class TestEventSourcedDomainEventRegistry:
    """Tests for EventSourcedDomainEventRegistry."""

    def test_register_and_get(self) -> None:
        """A registered class is retrievable by event_type."""
        registry = EventSourcedDomainEventRegistry()
        registry.register(
            ConcreteEventSourcedDomainEvent.event_type,
            ConcreteEventSourcedDomainEvent,
        )
        assert (
            registry.get(ConcreteEventSourcedDomainEvent.event_type)
            is ConcreteEventSourcedDomainEvent
        )

    def test_get_unknown_event_type_raises(self) -> None:
        """Looking up an unregistered event_type raises KeyError."""
        registry = EventSourcedDomainEventRegistry()
        with pytest.raises(KeyError):
            registry.get("no_such_event_type")

    def test_duplicate_event_type_raises(self) -> None:
        """Registering the same event_type twice raises TypeError."""
        registry = EventSourcedDomainEventRegistry()
        registry.register(
            ConcreteEventSourcedDomainEvent.event_type,
            ConcreteEventSourcedDomainEvent,
        )
        with pytest.raises(TypeError, match="already registered"):
            registry.register(
                ConcreteEventSourcedDomainEvent.event_type,
                ConcreteEventSourcedDomainEvent,
            )

    def test_each_instance_is_independent(self) -> None:
        """Two registry instances do not share state."""
        r1 = EventSourcedDomainEventRegistry()
        r2 = EventSourcedDomainEventRegistry()
        r1.register(
            ConcreteEventSourcedDomainEvent.event_type,
            ConcreteEventSourcedDomainEvent,
        )
        with pytest.raises(KeyError):
            r2.get(ConcreteEventSourcedDomainEvent.event_type)
