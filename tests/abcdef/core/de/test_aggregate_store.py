"""Tests for AggregateStore and Snapshot."""

from abcdef.core import Snapshot
from abcdef.in_memory import InMemoryAggregateStore
from tests.abcdef.conftest import make_id
from tests.abcdef.core.de.fixtures import DummyState


class TestSnapshot:
    """Tests for the Snapshot dataclass (repository-layer state record)."""

    def test_snapshot_creation(self) -> None:
        """Snapshot stores aggregate_id, event_version, and state."""
        agg_id = make_id()
        state = DummyState(count=42)
        snapshot = Snapshot(aggregate_id=agg_id, event_version=5, state=state)

        assert snapshot.aggregate_id == agg_id
        assert snapshot.event_version == 5
        assert snapshot.state.count == 42
        assert snapshot.timestamp is None

    def test_snapshot_with_timestamp(self) -> None:
        """Snapshot accepts an optional timestamp."""
        snapshot = Snapshot(
            aggregate_id=make_id(),
            event_version=3,
            state=DummyState(count=10),
            timestamp=1_700_000_000.0,
        )
        assert snapshot.timestamp == 1_700_000_000.0


class TestAggregateStore:
    """Tests for AggregateStore abstraction."""

    def test_save_and_retrieve_snapshot(self) -> None:
        """A saved state record can be retrieved."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        snapshot = Snapshot(
            aggregate_id=agg_id, event_version=10, state=DummyState(count=5)
        )

        store.save_snapshot(snapshot)
        result = store.get_latest_snapshot(agg_id)

        assert result is not None
        assert result.event_version == 10
        assert isinstance(result.state, DummyState)
        assert result.state.count == 5

    def test_get_latest_snapshot_missing(self) -> None:
        """Returns None when no state record exists for an aggregate."""
        store = InMemoryAggregateStore()
        result = store.get_latest_snapshot(make_id())
        assert result is None

    def test_save_overwrites_previous_snapshot(self) -> None:
        """Saving a second state record replaces the first."""
        store = InMemoryAggregateStore()
        agg_id = make_id()

        store.save_snapshot(
            Snapshot(aggregate_id=agg_id, event_version=5, state=DummyState(count=3))
        )
        store.save_snapshot(
            Snapshot(aggregate_id=agg_id, event_version=10, state=DummyState(count=8))
        )

        result = store.get_latest_snapshot(agg_id)
        assert result is not None
        assert result.event_version == 10
        assert isinstance(result.state, DummyState)
        assert result.state.count == 8

    def test_delete_snapshots(self) -> None:
        """Deleting state records removes them from the store."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save_snapshot(
            Snapshot(aggregate_id=agg_id, event_version=5, state=DummyState(count=3))
        )

        store.delete_snapshots(agg_id)

        assert store.get_latest_snapshot(agg_id) is None

    def test_delete_snapshots_nonexistent(self) -> None:
        """Deleting state records for an unknown aggregate does not raise."""
        store = InMemoryAggregateStore()
        store.delete_snapshots(make_id())

    def test_snapshots_isolated_per_aggregate(self) -> None:
        """State records for different aggregates do not interfere."""
        store = InMemoryAggregateStore()
        id_a = make_id()
        id_b = make_id()

        store.save_snapshot(
            Snapshot(aggregate_id=id_a, event_version=5, state=DummyState(count=1))
        )
        store.save_snapshot(
            Snapshot(aggregate_id=id_b, event_version=3, state=DummyState(count=99))
        )

        snapshot_a = store.get_latest_snapshot(id_a)
        snapshot_b = store.get_latest_snapshot(id_b)
        assert snapshot_a is not None
        assert snapshot_b is not None
        assert isinstance(snapshot_a.state, DummyState)
        assert isinstance(snapshot_b.state, DummyState)
        assert snapshot_a.state.count == 1
        assert snapshot_b.state.count == 99
