"""Tests for EventSourcedRepository."""

import pytest

from abcdef.core import Snapshot
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
        repo, event_store, _ = _make_repo()
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
        repo, _, _ = _make_repo()
        agg = DummyAggregate(make_id())
        agg.increment(1)

        repo.save(agg)

        assert len(agg._get_uncommitted_events()) == 0

    def test_save_with_no_events_is_a_no_op(self) -> None:
        """Saving an aggregate with no uncommitted events does nothing."""
        repo, event_store, _ = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)

        repo.save(agg)

        assert event_store.get_events(agg_id) == []

    def test_save_creates_state_record_at_threshold(self) -> None:
        """A state record is created when event delta reaches the threshold."""
        repo, _, aggregate_store = _make_repo(threshold=3)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)

        agg.increment(1)
        agg.increment(1)
        agg.increment(1)
        repo.save(agg)

        snapshot = aggregate_store.get_latest_snapshot(agg_id)
        assert snapshot is not None
        assert snapshot.event_version == 3
        assert isinstance(snapshot.state, DummyState)
        assert snapshot.state.count == 3

    def test_save_does_not_create_state_record_below_threshold(self) -> None:
        """No state record is created when event delta is below the threshold."""
        repo, _, aggregate_store = _make_repo(threshold=5)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        assert aggregate_store.get_latest_snapshot(agg_id) is None

    def test_save_uses_aggregate_delta_not_total_event_count(self) -> None:
        """State threshold is based on events since last state save, not total."""
        repo, _, aggregate_store = _make_repo(threshold=3)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)

        # First batch: 3 events -> state saved, base_version advances to 3
        agg.increment(1)
        agg.increment(1)
        agg.increment(1)
        repo.save(agg)
        assert aggregate_store.get_latest_snapshot(agg_id) is not None
        assert agg.base_version == 3

        # Second batch: 2 events -> delta is 2, below threshold -> no new state save
        agg.increment(1)
        agg.increment(1)
        repo.save(agg)
        snapshot = aggregate_store.get_latest_snapshot(agg_id)
        assert snapshot is not None
        assert snapshot.event_version == 3  # still the first state record

    def test_save_updates_base_version_after_state_save(self) -> None:
        """base_version is updated to current version after state is persisted."""
        repo, _, _ = _make_repo(threshold=2)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        assert agg.base_version == 2

    def test_save_state_version_matches_aggregate_version(self) -> None:
        """State record event_version equals the aggregate's version at save time."""
        repo, _, aggregate_store = _make_repo(threshold=2)
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(1)
        agg.increment(1)

        repo.save(agg)

        snapshot = aggregate_store.get_latest_snapshot(agg_id)
        assert snapshot is not None
        assert snapshot.event_version == agg.version


class TestEventSourcedRepositoryGetById:
    """Tests for EventSourcedRepository.get_by_id()."""

    def test_get_by_id_returns_none_for_unknown_aggregate(self) -> None:
        """Returns None when no events exist for the given ID."""
        repo, _, _ = _make_repo()
        result = repo.get_by_id(make_id())
        assert result is None

    def test_get_by_id_replays_all_events(self) -> None:
        """Aggregate is reconstructed by replaying all stored events."""
        repo, _, _ = _make_repo()
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        agg.increment(3)
        agg.increment(4)
        repo.save(agg)

        restored = repo.get_by_id(agg_id)

        assert restored is not None
        assert restored.count == 7

    def test_get_by_id_uses_state_record_and_delta(self) -> None:
        """When a state record exists, only events after it are replayed."""
        repo, event_store, aggregate_store = _make_repo(threshold=10)
        agg_id = make_id()

        # Inject a state record at version 2 with count=10
        aggregate_store.save_snapshot(
            Snapshot(
                aggregate_id=agg_id,
                event_version=2,
                state=DummyState(count=10),
            )
        )

        # Two pre-state events (already captured in state) then two delta events
        key = str(agg_id)
        event_store._store[key] = [
            DummyEvent(amount=5),  # version 1 - already in state record
            DummyEvent(amount=5),  # version 2 - already in state record
            DummyEvent(amount=1),  # delta - replayed
            DummyEvent(amount=2),  # delta - replayed
        ]

        restored = repo.get_by_id(agg_id)

        assert restored is not None
        assert restored.count == 13  # snapshot(10) + delta(1+2)
        assert restored.id == agg_id


class TestEventSourcedRepositoryNotImplemented:
    """Tests for operations not supported by pure event sourcing."""

    def test_delete_raises(self) -> None:
        """delete() raises NotImplementedError in pure event sourcing."""
        repo, _, _ = _make_repo()
        with pytest.raises(NotImplementedError):
            repo.delete(make_id())

    def test_find_all_raises(self) -> None:
        """find_all() raises NotImplementedError - requires projections."""
        repo, _, _ = _make_repo()
        with pytest.raises(NotImplementedError):
            repo.find_all()


class TestEventSourcedRepositoryStateStrategy:
    """Tests for the default state persistence strategy."""

    def test_should_save_state_at_exact_threshold(self) -> None:
        """State is saved when event count is exactly the threshold."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(5) is True

    def test_should_save_state_at_multiples(self) -> None:
        """State is saved at every multiple of the threshold."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(10) is True
        assert repo._should_save_state(15) is True

    def test_should_not_save_state_below_threshold(self) -> None:
        """No state save below the threshold."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(4) is False

    def test_should_not_save_state_at_zero(self) -> None:
        """No state save at zero events."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(0) is False

    def test_should_not_save_state_one_above_threshold(self) -> None:
        """No state save when event count is one above a threshold multiple."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(6) is False

    def test_should_not_save_state_one_below_threshold(self) -> None:
        """No state save when event count is one below a threshold multiple."""
        repo, _, _ = _make_repo(threshold=5)
        assert repo._should_save_state(9) is False

    def test_should_save_state_threshold_of_one(self) -> None:
        """Every event triggers a state save when threshold is 1."""
        repo, _, _ = _make_repo(threshold=1)
        assert repo._should_save_state(1) is True
        assert repo._should_save_state(2) is True
        assert repo._should_save_state(3) is True

    def test_should_not_save_state_zero_with_threshold_one(self) -> None:
        """Even with threshold=1, count=0 never triggers a state save."""
        repo, _, _ = _make_repo(threshold=1)
        assert repo._should_save_state(0) is False
