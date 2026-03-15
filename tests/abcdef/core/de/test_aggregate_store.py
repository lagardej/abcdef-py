"""Tests for AggregateStore and AggregateRecord."""

import pytest

from abcdef.core import AggregateRecord
from abcdef.core.de.aggregate_store import VersionConflictError
from abcdef.in_memory import InMemoryAggregateStore
from tests.abcdef.conftest import make_id
from tests.abcdef.core.de.fixtures import DummyState


class TestAggregateRecord:
    """Tests for the AggregateRecord dataclass."""

    def test_record_with_state(self) -> None:
        """AggregateRecord stores aggregate_id, event_version, and optional state."""
        agg_id = make_id()
        state = DummyState(count=42)
        record = AggregateRecord(
            aggregate_id=agg_id, aggregate_type="dummy", event_version=5, state=state
        )

        assert record.aggregate_id == agg_id
        assert record.event_version == 5
        assert record.state is not None
        assert record.state.count == 42
        assert record.timestamp is None

    def test_record_without_state(self) -> None:
        """AggregateRecord can be created without state (version tracking only)."""
        agg_id = make_id()
        record = AggregateRecord(
            aggregate_id=agg_id, aggregate_type="dummy", event_version=3
        )

        assert record.aggregate_id == agg_id
        assert record.event_version == 3
        assert record.state is None

    def test_record_with_timestamp(self) -> None:
        """AggregateRecord accepts an optional timestamp."""
        record = AggregateRecord(
            aggregate_id=make_id(),
            aggregate_type="dummy",
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
            aggregate_id=agg_id,
            aggregate_type="dummy",
            event_version=10,
            state=DummyState(count=5),
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

        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=2
            )
        )
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
                aggregate_id=agg_id,
                aggregate_type="dummy",
                event_version=5,
                state=DummyState(count=3),
            )
        )
        store.save(
            AggregateRecord(
                aggregate_id=agg_id,
                aggregate_type="dummy",
                event_version=10,
                state=DummyState(count=8),
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
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=5
            )
        )

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
                aggregate_id=id_a,
                aggregate_type="dummy",
                event_version=5,
                state=DummyState(count=1),
            )
        )
        store.save(
            AggregateRecord(
                aggregate_id=id_b,
                aggregate_type="dummy",
                event_version=3,
                state=DummyState(count=99),
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


class TestVersionConflict:
    """Tests for optimistic concurrency via expected_version."""

    def test_save_with_correct_expected_version_succeeds(self) -> None:
        """Saving with the correct expected_version does not raise."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=1
            )
        )

        # Store is at version 1; saving with expected_version=1 should succeed.
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=2
            ),
            expected_version=1,
        )

        result = store.get(agg_id)
        assert result is not None
        assert result.event_version == 2

    def test_save_with_stale_expected_version_raises(self) -> None:
        """Saving with a stale expected_version raises VersionConflictError."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=3
            )
        )

        # Store is at version 3, but caller expects version 1.
        with pytest.raises(VersionConflictError) as exc_info:
            store.save(
                AggregateRecord(
                    aggregate_id=agg_id, aggregate_type="dummy", event_version=4
                ),
                expected_version=1,
            )

        assert exc_info.value.expected == 1
        assert exc_info.value.actual == 3

    def test_save_with_none_expected_version_skips_check(self) -> None:
        """expected_version=None bypasses the conflict check."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=5
            )
        )

        # Should not raise regardless of stored version.
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=6
            ),
            expected_version=None,
        )

        result = store.get(agg_id)
        assert result is not None
        assert result.event_version == 6

    def test_save_new_aggregate_with_expected_version_zero_succeeds(self) -> None:
        """expected_version=0 succeeds when no record exists yet."""
        store = InMemoryAggregateStore()
        agg_id = make_id()

        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=1
            ),
            expected_version=0,
        )

        assert store.get(agg_id) is not None

    def test_save_new_aggregate_with_wrong_expected_version_raises(self) -> None:
        """expected_version > 0 raises when no record exists yet."""
        store = InMemoryAggregateStore()
        agg_id = make_id()

        with pytest.raises(VersionConflictError) as exc_info:
            store.save(
                AggregateRecord(
                    aggregate_id=agg_id, aggregate_type="dummy", event_version=1
                ),
                expected_version=3,
            )

        assert exc_info.value.expected == 3
        assert exc_info.value.actual == 0

    def test_conflict_does_not_overwrite_existing_record(self) -> None:
        """On conflict, the existing record is left unchanged."""
        store = InMemoryAggregateStore()
        agg_id = make_id()
        store.save(
            AggregateRecord(
                aggregate_id=agg_id, aggregate_type="dummy", event_version=2
            )
        )

        with pytest.raises(VersionConflictError):
            store.save(
                AggregateRecord(
                    aggregate_id=agg_id, aggregate_type="dummy", event_version=99
                ),
                expected_version=0,
            )

        result = store.get(agg_id)
        assert result is not None
        assert result.event_version == 2
