"""Shared fixtures for de/ tests."""

import datetime

from abcdef.core import AggregateId, AggregateState, DomainEvent, EventSourcedAggregate
from abcdef.core.de import EventSourcedRepository
from abcdef.in_memory import InMemoryAggregateStore, InMemoryEventStore

_TS = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)
_DEFAULT_AGG_ID = "test-aggregate"

# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


class DummyIncrementedEvent(DomainEvent):
    """Dummy increment event."""

    event_type = "dummy_incremented"

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        self.amount = amount


class DummyDecrementedEvent(DomainEvent):
    """Dummy decrement event."""

    event_type = "dummy_decremented"

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        self.amount = amount


class DummyEvent(DomainEvent):
    """Generic dummy event used in repository tests."""

    event_type = "dummy_event"

    def __init__(self, amount: int, aggregate_id: str = _DEFAULT_AGG_ID) -> None:
        """Initialise with an amount and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        self.amount = amount


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------


class DummyState(AggregateState):
    """Dummy aggregate state."""

    def __init__(self, count: int) -> None:
        """Initialise with a count."""
        self.count = count


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


class DummyAggregate(EventSourcedAggregate[DummyState]):
    """Dummy event-sourced aggregate supporting increment and decrement."""

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

    def _apply_event(self, event: DomainEvent) -> None:
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

    def build_from_events(
        self, aggregate_id: AggregateId, events: list[DomainEvent]
    ) -> DummyAggregate:
        """Reconstruct a DummyAggregate from its full event history."""
        agg = DummyAggregate(aggregate_id)
        agg._load_from_history(events)
        return agg

    def _create_from_state(
        self, aggregate_id: AggregateId, state: object, version: int
    ) -> DummyAggregate:
        """Reconstruct a DummyAggregate from a state record."""
        assert isinstance(state, DummyState)
        agg = DummyAggregate.from_state(aggregate_id, state, version)
        assert isinstance(agg, DummyAggregate)
        return agg


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def make_repo(
    threshold: int = 10,
) -> tuple[DummyRepository, InMemoryEventStore, InMemoryAggregateStore]:
    """Create a DummyRepository with in-memory stores."""
    event_store = InMemoryEventStore()
    aggregate_store = InMemoryAggregateStore()
    repo = DummyRepository(
        event_store,
        aggregate_store,
        snapshot_threshold=threshold,
    )
    return repo, event_store, aggregate_store


__all__ = [
    "DummyAggregate",
    "DummyDecrementedEvent",
    "DummyEvent",
    "DummyIncrementedEvent",
    "DummyRepository",
    "DummyState",
    "make_repo",
]
