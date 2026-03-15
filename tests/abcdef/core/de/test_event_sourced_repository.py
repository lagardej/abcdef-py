"""Tests for EventSourcedRepository."""

import pytest

from abcdef.core import AggregateRecord, DomainEvent
from abcdef.core.de.aggregate_store import VersionConflictError
from tests.abcdef.conftest import make_id
from tests.abcdef.core.de.fixtures import (
    DummyAggregate,
    DummyEvent,
    DummyIncrementedEvent,
    DummyState,
)
from tests.abcdef.core.de.fixtures import (
    make_repo as _make_repo,
)


class TestEventSourcedRepositorySave:
    """Tests for EventSourcedRepository.save()."""

    def test_save_appends_events_to_store(self) -> None:
        """Uncommitted events are persisted to the event store on save."""
        repo, event_store, _, _ = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(5)

        repo.save(agg)

        stored = event_store.get_events(agg_id)
        assert len(stored) == 1
        assert isinstance(stored[0], DummyIncrementedEvent)
        assert stored[0].amount == 5

    def test_save_marks_events_as_committed(self) -> None:
        """After save, the aggregate has no uncommitted events."""
        repo, _, _, _ = _make_repo()
        agg = DummyAggregate(make_id())
        agg.increment(1)

        repo.save(agg)

        assert len(agg._get_uncommitted_events()) == 0

    def test_save_with_no_events_is_a_no_op(self) -> None:
        """Saving an aggregate with no uncommitted events does nothing."""
        repo, event_store, aggregate_store, _ = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)

        repo.save(agg)

        assert event_store.get_events(agg_id) == []
        assert aggregate_store.get(agg_id) is None

    def test_save_always_writes_aggregate_record(self) -> None:
        """An aggregate record is written on every save, regardless of threshold."""
        repo, _, aggregate_store, _ = _make_repo(threshold=10)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)

        repo.save(agg)

        record = aggregate_store.get(agg_id)
        assert record is not None
        assert record.event_version == 1

    def test_save_record_has_no_state_below_threshold(self) -> None:
        """Record written below threshold carries no state."""
        repo, _, aggregate_store, _ = _make_repo(threshold=5)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        record = aggregate_store.get(agg_id)
        assert record is not None
        assert record.state is None

    def test_save_record_has_state_at_threshold(self) -> None:
        """Record written at threshold carries a state snapshot."""
        repo, _, aggregate_store, _ = _make_repo(threshold=3)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        record = aggregate_store.get(agg_id)
        assert record is not None
        assert record.event_version == 3
        assert isinstance(record.state, DummyState)
        assert record.state.count == 3

    def test_save_uses_aggregate_delta_not_total_event_count(self) -> None:
        """State threshold is based on events since last state save, not total."""
        repo, _, aggregate_store, _ = _make_repo(threshold=3)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)

        # First batch: 3 events -> state written, base_version advances to 3
        agg.increment(1)
        agg.increment(1)
        agg.increment(1)
        repo.save(agg)
        assert aggregate_store.get(agg_id) is not None
        assert agg.base_version == 3

        # Second batch: 2 events -> delta is 2, below threshold -> no state
        agg.increment(1)
        agg.increment(1)
        repo.save(agg)
        record = aggregate_store.get(agg_id)
        assert record is not None
        assert record.event_version == 5  # updated to current version
        assert record.state is None  # no state below threshold

    def test_save_updates_base_version_after_state_written(self) -> None:
        """base_version is updated to current version after state is persisted."""
        repo, _, _, _ = _make_repo(threshold=2)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        assert agg.base_version == 2

    def test_save_record_version_matches_aggregate_version(self) -> None:
        """Record event_version equals the aggregate's version at save time."""
        repo, _, aggregate_store, _ = _make_repo(threshold=2)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        record = aggregate_store.get(agg_id)
        assert record is not None
        assert record.event_version == agg.version

    def test_save_raises_on_concurrent_write(self) -> None:
        """save() raises VersionConflictError when another writer has already committed.

        Simulates two writers loading the same aggregate at version 0, both emitting
        events. The first save succeeds and advances the record to version 1. The
        second save carries expected_version=0, which no longer matches, and must raise.
        """
        repo, _, _, _ = _make_repo()
        agg_id = make_id()

        # Writer A: load at version 0, emit, save -- advances record to version 1.
        agg_a = DummyAggregate(agg_id)
        agg_a.increment(1)
        repo.save(agg_a)

        # Writer B: also started from version 0, emits a different event.
        agg_b = DummyAggregate(agg_id)
        agg_b.increment(99)

        # agg_b.version == 1, len(uncommitted) == 1 -> expected_version == 0
        # Record is already at version 1, so this must raise.
        with pytest.raises(VersionConflictError):
            repo.save(agg_b)


class TestEventSourcedRepositoryEventBus:
    """Tests for event publishing after save."""

    def test_save_publishes_committed_events_to_bus(self) -> None:
        """Events are published to the bus after a successful save."""
        repo, _, _, bus = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(3)

        published: list[DomainEvent] = []
        bus.subscribe(DummyIncrementedEvent, published.append)

        repo.save(agg)

        assert len(published) == 1
        assert isinstance(published[0], DummyIncrementedEvent)
        assert published[0].amount == 3

    def test_save_publishes_events_in_order(self) -> None:
        """Multiple events are published in emission order."""
        repo, _, _, bus = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(2)
        agg.increment(3)

        published: list[DomainEvent] = []
        bus.subscribe(DummyIncrementedEvent, published.append)

        repo.save(agg)

        assert len(published) == 3
        amounts = [e.amount for e in published if isinstance(e, DummyIncrementedEvent)]
        assert amounts == [1, 2, 3]

    def test_save_no_op_does_not_publish(self) -> None:
        """No events are published when save is a no-op (no uncommitted events)."""
        repo, _, _, bus = _make_repo()
        agg = DummyAggregate(make_id())

        published: list[DomainEvent] = []
        bus.subscribe(DummyIncrementedEvent, published.append)

        repo.save(agg)

        assert published == []


class TestEventSourcedRepositoryGetById:
    """Tests for EventSourcedRepository.get_by_id()."""

    def test_get_by_id_returns_none_for_unknown_aggregate(self) -> None:
        """Returns None when no events exist for the given ID."""
        repo, _, _, _ = _make_repo()
        result = repo.get_by_id(make_id())
        assert result is None

    def test_get_by_id_replays_all_events(self) -> None:
        """Aggregate is reconstructed by replaying all stored events."""
        repo, _, _, _ = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(3)
        agg.increment(4)
        repo.save(agg)

        restored = repo.get_by_id(agg_id)

        assert restored is not None
        assert restored.count == 7

    def test_get_by_id_uses_state_and_delta_when_state_present(self) -> None:
        """When a record with state exists, only events after it are replayed."""
        repo, event_store, aggregate_store, _ = _make_repo(threshold=10)
        agg_id = make_id()

        # Inject a record with state at version 2
        aggregate_store.save(
            AggregateRecord(
                aggregate_id=agg_id,
                aggregate_type=DummyAggregate.aggregate_type,
                event_version=2,
                state=DummyState(count=10),
            )
        )

        injected: list[DomainEvent] = [
            DummyEvent(amount=5),  # version 1 - captured in state
            DummyEvent(amount=5),  # version 2 - captured in state
            DummyEvent(amount=1),  # delta - replayed
            DummyEvent(amount=2),  # delta - replayed
        ]
        event_store._store[str(agg_id)] = injected

        restored = repo.get_by_id(agg_id)

        assert restored is not None
        assert restored.count == 13  # state(10) + delta(1+2)
        assert restored.id == agg_id

    def test_get_by_id_replays_all_events_when_record_has_no_state(self) -> None:
        """When a record exists but has no state, all events are replayed."""
        repo, event_store, aggregate_store, _ = _make_repo(threshold=10)
        agg_id = make_id()

        # Record present but no state (below threshold)
        aggregate_store.save(
            AggregateRecord(
                aggregate_id=agg_id,
                aggregate_type=DummyAggregate.aggregate_type,
                event_version=2,
            )
        )

        injected: list[DomainEvent] = [
            DummyEvent(amount=5),
            DummyEvent(amount=5),
        ]
        event_store._store[str(agg_id)] = injected

        restored = repo.get_by_id(agg_id)

        assert restored is not None
        assert restored.count == 10


class TestEventSourcedRepositoryAggregateType:
    """Tests for aggregate_type enforcement on EventSourcedRepository subclasses."""

    def test_concrete_subclass_without_aggregate_type_raises(self) -> None:
        """Defining a repository subclass without aggregate_type raises TypeError."""
        from abcdef.core.de import EventSourcedRepository

        with pytest.raises(TypeError, match="aggregate_type"):

            class NoTypeRepo(EventSourcedRepository):  # type: ignore[type-arg]
                pass


class TestEventSourcedRepositoryNotImplemented:
    """Tests for operations not supported by pure event sourcing."""

    def test_delete_raises(self) -> None:
        """delete() raises NotImplementedError in pure event sourcing."""
        repo, _, _, _ = _make_repo()
        with pytest.raises(NotImplementedError):
            repo.delete(make_id())

    def test_find_all_raises(self) -> None:
        """find_all() raises NotImplementedError - requires projections."""
        repo, _, _, _ = _make_repo()
        with pytest.raises(NotImplementedError):
            repo.find_all()
