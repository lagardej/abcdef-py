"""Shared fixtures for de/ tests."""

import datetime
from dataclasses import dataclass

from abcdef.d import AggregateId
from abcdef.de import (
    AggregateRegistry,
    AggregateState,
    EventSourcedAggregate,
    EventSourcedDomainEvent,
    EventSourcedRepository,
)
from abcdef.in_memory import (
    InMemoryAggregateStore,
    InMemoryEventStore,
)
from abcdef.in_memory.event_bus import InMemoryEventBus

_TS = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)
_DEFAULT_AGG_ID = "test-aggregate"

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class DummyIncrementedEvent(EventSourcedDomainEvent):
    """Dummy increment event."""

    event_type = "dummy_incremented"
    amount: int

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        object.__setattr__(self, "amount", amount)


class DummyDecrementedEvent(EventSourcedDomainEvent):
    """Dummy decrement event."""

    event_type = "dummy_decremented"
    amount: int

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        object.__setattr__(self, "amount", amount)


class DummyEvent(EventSourcedDomainEvent):
    """Generic dummy event used in repository tests."""

    event_type = "dummy_event"
    amount: int

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        object.__setattr__(self, "amount", amount)


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DummyState(AggregateState):
    """Dummy aggregate state."""

    count: int


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


class DummyAggregate(EventSourcedAggregate[DummyState]):
    """Dummy event-sourced aggregate supporting increment and decrement."""

    aggregate_type = "dummy_aggregate"

    def __init__(self, aggregate_id: AggregateId, count: int = 0) -> None:
        """Initialise with an aggregate_id and optional count."""
        super().__init__(aggregate_id)
        self.count = count

    def increment(self, amount: int) -> None:
        """Emit a DummyIncrementedEvent."""
        self._emit_event(DummyIncrementedEvent(amount, aggregate_id=str(self.id)))

    def decrement(self, amount: int) -> None:
        """Emit a DummyDecrementedEvent."""
        self._emit_event(DummyDecrementedEvent(amount, aggregate_id=str(self.id)))

    def _apply_event(self, event: EventSourcedDomainEvent) -> None:
        """Apply events to state."""
        if isinstance(event, DummyIncrementedEvent):
            self.count += event.amount
        elif isinstance(event, DummyDecrementedEvent):
            self.count -= event.amount
        elif isinstance(event, DummyEvent):
            self.count += event.amount

    def create_state(self) -> DummyState:
        """Capture current state."""
        return DummyState(count=self.count)

    def load_from_state(self, state: DummyState) -> None:
        """Restore state from a state record."""
        self.count = state.count


# ---------------------------------------------------------------------------
# Repository
# ---------------------------------------------------------------------------


class DummyRepository(EventSourcedRepository[AggregateId, DummyAggregate]):
    """Concrete repository for de/ tests."""

    aggregate_type = "dummy_aggregate"


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def make_repo(
    threshold: int = 10,
) -> tuple[
    DummyRepository, InMemoryEventStore, InMemoryAggregateStore, InMemoryEventBus
]:
    """Create a DummyRepository with in-memory stores and an event bus.

    Constructs a fresh AggregateRegistry populated with DummyAggregate
    and passes it to the repository.
    """
    event_store = InMemoryEventStore()
    aggregate_store = InMemoryAggregateStore()
    event_bus: InMemoryEventBus[EventSourcedDomainEvent] = InMemoryEventBus()
    registry = AggregateRegistry()
    registry.register(DummyAggregate.aggregate_type, DummyAggregate)
    repo = DummyRepository(
        event_store,
        aggregate_store,
        event_bus,
        registry,
        snapshot_threshold=threshold,
    )
    return repo, event_store, aggregate_store, event_bus


__all__ = [
    "DummyAggregate",
    "DummyDecrementedEvent",
    "DummyEvent",
    "DummyIncrementedEvent",
    "DummyRepository",
    "DummyState",
    "make_repo",
]
