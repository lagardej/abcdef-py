"""Tests for Aggregate Root and Aggregate ID."""

from uuid import UUID

import pytest

from abcdef.core import AggregateId
from tests.abcdef.conftest import make_id
from tests.abcdef.core.d.fixtures import DummyAggregate


class TestAggregateId:
    """Tests for AggregateId."""

    def test_default_generates_uuid(self) -> None:
        """AggregateId() with no args generates a UUID."""
        agg_id = AggregateId()
        assert isinstance(agg_id.value, UUID)

    def test_two_defaults_are_distinct(self) -> None:
        """Two AggregateId() calls produce different IDs."""
        assert AggregateId() != AggregateId()

    def test_accepts_uuid_object(self) -> None:
        """AggregateId accepts a UUID directly."""
        uid = UUID("12345678-1234-5678-1234-567812345678")
        agg_id = AggregateId(uid)
        assert agg_id.value == uid

    def test_accepts_uuid_string(self) -> None:
        """AggregateId coerces a UUID string to UUID."""
        uid_str = "12345678-1234-5678-1234-567812345678"
        agg_id = AggregateId(uid_str)
        assert isinstance(agg_id.value, UUID)
        assert str(agg_id.value) == uid_str

    def test_rejects_non_uuid_string(self) -> None:
        """AggregateId raises ValueError for strings that are not valid UUIDs."""
        with pytest.raises(ValueError):
            AggregateId("not-a-uuid")

    def test_string_representation(self) -> None:
        """str() returns the canonical UUID string."""
        uid_str = "12345678-1234-5678-1234-567812345678"
        agg_id = AggregateId(uid_str)
        assert str(agg_id) == uid_str

    def test_equality_by_value(self) -> None:
        """Two AggregateIds with the same UUID are equal."""
        uid = UUID("12345678-1234-5678-1234-567812345678")
        assert AggregateId(uid) == AggregateId(uid)

    def test_inequality_by_value(self) -> None:
        """Two AggregateIds with different UUIDs are not equal."""
        assert AggregateId() != AggregateId()

    def test_immutable(self) -> None:
        """AggregateId is immutable."""
        agg_id = AggregateId()
        with pytest.raises(AttributeError, match="immutable"):
            agg_id.value = UUID("12345678-1234-5678-1234-567812345678")  # type: ignore[misc]

    def test_hashable(self) -> None:
        """AggregateId can be used in sets and dicts."""
        id1 = make_id()
        id2 = make_id()
        assert len({id1, id2}) == 2

    def test_hash_consistent_with_equality(self) -> None:
        """Equal AggregateIds have the same hash."""
        uid = UUID("12345678-1234-5678-1234-567812345678")
        assert hash(AggregateId(uid)) == hash(AggregateId(uid))


class TestAggregateRoot:
    """Tests for AggregateRoot."""

    def test_id_property(self) -> None:
        """Id property returns the AggregateId passed at construction."""
        agg_id = make_id()
        agg = DummyAggregate(agg_id, "Test")
        assert agg.id is agg_id

    def test_equality_by_id(self) -> None:
        """Aggregates with the same ID are equal regardless of other state."""
        agg_id = make_id()
        assert DummyAggregate(agg_id, "A") == DummyAggregate(agg_id, "B")

    def test_inequality_by_id(self) -> None:
        """Aggregates with different IDs are not equal."""
        assert DummyAggregate(make_id()) != DummyAggregate(make_id())

    def test_cross_type_inequality(self) -> None:
        """Equality returns NotImplemented for objects of different types."""
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        assert agg.__eq__("not an aggregate") is NotImplemented

    def test_hashable(self) -> None:
        """Aggregates can be used in sets and dicts."""
        agg1 = DummyAggregate(make_id())
        agg2 = DummyAggregate(make_id())
        assert len({agg1, agg2}) == 2

    def test_hash_equals_id_hash(self) -> None:
        """hash(aggregate) equals hash(aggregate.id)."""
        agg_id = make_id()
        agg = DummyAggregate(agg_id)
        assert hash(agg) == hash(agg_id)

    def test_hash_consistent_across_instances(self) -> None:
        """Two aggregates with the same ID have the same hash."""
        agg_id = make_id()
        assert hash(DummyAggregate(agg_id)) == hash(DummyAggregate(agg_id))

    def test_hash_differs_for_different_ids(self) -> None:
        """Aggregates with different IDs produce different hashes."""
        assert hash(DummyAggregate(make_id())) != hash(DummyAggregate(make_id()))
