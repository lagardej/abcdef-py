"""Tests for Aggregate Root and Aggregate ID."""

from abcdef.core import AggregateId
from tests.abcdef.conftest import StrAggregateId, make_id
from tests.abcdef.core.d.fixtures import DummyAggregate


class TestAggregateIdSerialisation:
    """Tests for the AggregateId serialisation contract.

    Uses StrAggregateId — a minimal string-backed concrete implementation
    defined in conftest — to exercise the abstract contract without coupling
    the tests to any production implementation.
    """

    def test_str_returns_string(self) -> None:
        """str() returns a non-empty string."""
        agg_id = StrAggregateId("abc")
        assert isinstance(str(agg_id), str)
        assert str(agg_id) == "abc"

    def test_from_str_round_trips(self) -> None:
        """from_str(str(id)) produces an equal ID."""
        original = StrAggregateId("abc")
        restored = StrAggregateId.from_str(str(original))
        assert original == restored

    def test_equality_same_value(self) -> None:
        """Two IDs with the same string are equal."""
        assert StrAggregateId("x") == StrAggregateId("x")

    def test_inequality_different_value(self) -> None:
        """Two IDs with different strings are not equal."""
        assert StrAggregateId("x") != StrAggregateId("y")

    def test_is_aggregate_id(self) -> None:
        """StrAggregateId is an instance of AggregateId."""
        assert isinstance(StrAggregateId("x"), AggregateId)

    def test_hashable(self) -> None:
        """AggregateId instances can be used in sets and dicts."""
        id1 = make_id()
        id2 = make_id()
        assert len({id1, id2}) == 2

    def test_hash_consistent_with_equality(self) -> None:
        """Equal AggregateIds have the same hash."""
        assert hash(StrAggregateId("abc")) == hash(StrAggregateId("abc"))


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
