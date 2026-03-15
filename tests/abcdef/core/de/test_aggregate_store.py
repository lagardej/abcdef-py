"""Tests for AggregateStore and AggregateRecord."""

from abcdef.core import AggregateRecord
from abcdef.in_memory import InMemoryAggregateStore
from tests.abcdef.conftest import make_id
from tests.abcdef.core.de.fixtures import DummyState


class TestAggregateRecord:
    """Tests for the AggregateRecord dataclass."""

    def test_record_with_state(self) -> None:
        """AggregateRecord stores aggregate_id, event_version, and optional state."""
        agg_id = make_id()
        state = DummyState(count=42)
        record = AggregateRecord(aggregate_id=agg_id, event_version=5, state=state)

        assert record.aggregate_id == agg_id
        assert record.event_version == 5
        assert record.state is not None
        assert record.state.count == 42
        assert record.timestamp is None

    def test_record_without_state(self) -> None:
        """AggregateRecord can be created without state (version tracking only)."""
        agg_id = make_id()
        record = AggregateRecord(aggregate_id=agg_id, event_version=3)

        assert record.aggregate_id == agg_id
        assert record.event_version == 3
        assert record.state is None

    def test_record_with_timestamp(self) -> None:
        """AggregateRecord accepts an optional timestamp."""
        record = AggregateRecord(
            aggregate_id=make_id(),
            event_version=3,
            timestamp=1_700_000_000.0,
        )
        assert record.timestamp == 1_700_000_000.0


class TestAggregateStore:
    """Tests for AggregateStore abstraction."""

    def test_save_and_retrieve_record(self) -> None:
        """A saved record can be retrieved."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        record = AggregateRecord(
            aggregate_id=agg_id, event_version=10, state=DummyState(count=5)
        )

        store.save(record)
        result = store.get(agg_id)

        assert result is not None
        assert result.event_version == 10
        assert result.state is not None
        assert isinstance(result.state, DummyState)
        assert result.state.count == 5

    def test_save_and_retrieve_record_without_state(self) -> None:
        """A record saved without state can be retrieved and has no state."""
        store = InMemoryAggregateStore()
        agg_id = make_id()

        store.save(AggregateRecord(aggregate_id=agg_id, event_version=2))
        result = store.get(agg_id)

        assert result is not None
        assert result.event_version == 2
        assert result.state is None

    def test_get_missing_returns_none(self) -> None:
        """Returns None when no record exists for an aggregate."""
        store = InMemoryAggregateStore()
        result = store.get(make_id())
        assert result is None

    def test_save_overwrites_previous_record(self) -> None:
        """Saving a second record replaces the first."""
        store = InMemoryAggregateStore()
        agg_id = make_id()

        store.save(
            AggregateRecord(
                aggregate_id=agg_id, event_version=5, state=DummyState(count=3)
            )
        )
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, event_version=10, state=DummyState(count=8)
            )
        )

        result = store.get(agg_id)
        assert result is not None
        assert result.event_version == 10
        assert result.state is not None
        assert isinstance(result.state, DummyState)
        assert result.state.count == 8

    def test_delete_record(self) -> None:
        """Deleting a record removes it from the store."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save(AggregateRecord(aggregate_id=agg_id, event_version=5))

        store.delete(agg_id)

        assert store.get(agg_id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        """Deleting a record for an unknown aggregate does not raise."""
        store = InMemoryAggregateStore()
        store.delete(make_id())

    def test_records_isolated_per_aggregate(self) -> None:
        """Records for different aggregates do not interfere."""
        store = InMemoryAggregateStore()
        id_a = make_id()
        id_b = make_id()

        store.save(
            AggregateRecord(
                aggregate_id=id_a, event_version=5, state=DummyState(count=1)
            )
        )
        store.save(
            AggregateRecord(
                aggregate_id=id_b, event_version=3, state=DummyState(count=99)
            )
        )

        record_a = store.get(id_a)
        record_b = store.get(id_b)
        assert record_a is not None
        assert record_b is not None
        assert record_a.state is not None
        assert record_b.state is not None
        assert isinstance(record_a.state, DummyState)
        assert isinstance(record_b.state, DummyState)
        assert record_a.state.count == 1
        assert record_b.state.count == 99
