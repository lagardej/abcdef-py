"""Tests for EventSourcedAggregate."""

import pytest

from abcdef.de import (
    AggregateRegistry,
    AggregateState,
    EventSourcedAggregate,
)
from tests.abcdef.conftest import make_id
from tests.abcdef.de.fixtures import (
    DummyAggregate,
    DummyIncrementedEvent,
    DummyState,
)


class TestAggregateState:
    """Tests for AggregateState base class."""

    def test_is_frozen_dataclass(self) -> None:
        """AggregateState subclass instances are immutable."""
        state = DummyState(count=10)
        with pytest.raises(AttributeError):
            state.count = 99  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        """Two instances with identical fields are equal."""
        assert DummyState(count=5) == DummyState(count=5)

    def test_inequality_by_value(self) -> None:
        """Two instances with different fields are not equal."""
        assert DummyState(count=5) != DummyState(count=6)

    def test_repr_contains_field_values(self) -> None:
        """repr() includes the class name and field values."""
        state = DummyState(count=42)
        assert "DummyState" in repr(state)
        assert "42" in repr(state)

    def test_is_aggregate_state_instance(self) -> None:
        """DummyState is an instance of AggregateState."""
        assert isinstance(DummyState(count=0), AggregateState)

    def test_hashable(self) -> None:
        """Frozen dataclass state instances are hashable."""
        state = DummyState(count=7)
        assert isinstance(hash(state), int)

    def test_hash_consistent_with_equality(self) -> None:
        """Equal state instances have the same hash."""
        assert hash(DummyState(count=3)) == hash(DummyState(count=3))


class TestEventSourcedAggregate:
    """Tests for EventSourcedAggregate."""

    def test_initial_version_is_zero(self) -> None:
        """Version starts at zero before any events."""
        agg = DummyAggregate(make_id())
        assert agg.version == 0

    def test_emit_event_increments_version(self) -> None:
        """Each emitted event increments the version by one."""
        agg = DummyAggregate(make_id())
        agg.increment(1)
        assert agg.version == 1
        agg.increment(1)
        assert agg.version == 2

    def test_emit_event_applies_to_state(self) -> None:
        """Emitting an event immediately updates the aggregate's state."""
        agg = DummyAggregate(make_id())
        agg.increment(5)
        assert agg.count == 5

    def test_emit_multiple_events_accumulates_state(self) -> None:
        """Multiple events accumulate state correctly."""
        agg = DummyAggregate(make_id())
        agg.increment(10)
        agg.decrement(3)
        agg.increment(2)
        assert agg.count == 9
        assert agg.version == 3

    def test_emit_event_records_for_persistence(self) -> None:
        """Emitted events are recorded as uncommitted."""
        agg = DummyAggregate(make_id())
        agg.increment(1)
        agg.increment(2)
        events = agg._get_uncommitted_events()
        assert len(events) == 2
        assert isinstance(events[0], DummyIncrementedEvent)
        assert isinstance(events[1], DummyIncrementedEvent)

    def test_mark_events_committed_clears_uncommitted(self) -> None:
        """After commit, uncommitted event list is empty."""
        agg = DummyAggregate(make_id())
        agg.increment(1)
        agg._mark_events_as_committed()
        assert len(agg._get_uncommitted_events()) == 0

    def test_version_unchanged_after_commit(self) -> None:
        """Version is not reset or altered after committing events."""
        agg = DummyAggregate(make_id())
        agg.increment(1)
        agg.increment(1)
        agg._mark_events_as_committed()
        assert agg.version == 2

    def test_create_state_reflects_current_state(self) -> None:
        """create_state returns a snapshot of the current aggregate state."""
        agg = DummyAggregate(make_id())
        agg.increment(7)
        agg.decrement(2)
        state = agg.create_state()
        assert isinstance(state, DummyState)
        assert state.count == 5

    def test_apply_event_is_abstract(self) -> None:
        """EventSourcedAggregate cannot be instantiated without _apply_event."""
        with pytest.raises(TypeError):
            EventSourcedAggregate(make_id())  # type: ignore[abstract]


class TestAggregateRegistry:
    """Tests for AggregateRegistry."""

    def test_register_and_get(self) -> None:
        """A registered class is retrievable by aggregate_type."""
        registry = AggregateRegistry()
        registry.register(DummyAggregate.aggregate_type, DummyAggregate)
        assert registry.get(DummyAggregate.aggregate_type) is DummyAggregate

    def test_get_unknown_raises(self) -> None:
        """Looking up an unregistered aggregate_type raises KeyError."""
        registry = AggregateRegistry()
        with pytest.raises(KeyError):
            registry.get("no_such_type")

    def test_duplicate_registration_raises(self) -> None:
        """Registering the same aggregate_type twice raises TypeError."""
        registry = AggregateRegistry()
        registry.register(DummyAggregate.aggregate_type, DummyAggregate)
        with pytest.raises(TypeError, match="already registered"):
            registry.register(DummyAggregate.aggregate_type, DummyAggregate)

    def test_each_instance_is_independent(self) -> None:
        """Two registry instances do not share state."""
        r1 = AggregateRegistry()
        r2 = AggregateRegistry()
        r1.register(DummyAggregate.aggregate_type, DummyAggregate)
        with pytest.raises(KeyError):
            r2.get(DummyAggregate.aggregate_type)


class TestEventSourcedAggregateLoadFromHistory:
    """Tests for EventSourcedAggregate._load_from_history()."""

    def test_load_from_history_applies_events(self) -> None:
        """_load_from_history applies all events and updates state."""
        agg = DummyAggregate(make_id())
        events = [DummyIncrementedEvent(amount=3), DummyIncrementedEvent(amount=4)]

        agg._load_from_history(events)

        assert agg.count == 7

    def test_load_from_history_increments_version(self) -> None:
        """_load_from_history increments version once per event."""
        agg = DummyAggregate(make_id())
        events = [DummyIncrementedEvent(amount=1), DummyIncrementedEvent(amount=1)]

        agg._load_from_history(events)

        assert agg.version == 2

    def test_load_from_history_does_not_record_uncommitted_events(self) -> None:
        """Events loaded from history are not added to uncommitted events."""
        agg = DummyAggregate(make_id())
        agg._load_from_history([DummyIncrementedEvent(amount=1)])

        assert agg._get_uncommitted_events() == []

    def test_load_from_history_empty_list_is_no_op(self) -> None:
        """Loading an empty history leaves state and version unchanged."""
        agg = DummyAggregate(make_id())
        agg._load_from_history([])

        assert agg.version == 0
        assert agg.count == 0


class TestEventSourcedAggregateFromState:
    """Tests for EventSourcedAggregate.from_state()."""

    def test_from_state_restores_state(self) -> None:
        """from_state calls load_from_state with the provided state."""
        agg_id = make_id()
        state = DummyState(count=42)
        agg = DummyAggregate.from_state(agg_id, state, version=5)
        assert isinstance(agg, DummyAggregate)
        assert agg.count == 42

    def test_from_state_sets_version(self) -> None:
        """from_state sets version to the given version."""
        agg_id = make_id()
        state = DummyState(count=0)
        agg = DummyAggregate.from_state(agg_id, state, version=7)
        assert agg.version == 7

    def test_from_state_sets_base_version(self) -> None:
        """from_state sets base_version equal to version."""
        agg_id = make_id()
        state = DummyState(count=0)
        agg = DummyAggregate.from_state(agg_id, state, version=7)
        assert agg.base_version == 7

    def test_from_state_sets_id(self) -> None:
        """from_state sets the aggregate id correctly."""
        agg_id = make_id()
        state = DummyState(count=0)
        agg = DummyAggregate.from_state(agg_id, state, version=3)
        assert agg.id == agg_id

    def test_from_state_has_no_uncommitted_events(self) -> None:
        """Aggregate reconstructed from state has no uncommitted events."""
        agg_id = make_id()
        state = DummyState(count=10)
        agg = DummyAggregate.from_state(agg_id, state, version=5)
        assert agg._get_uncommitted_events() == []

    def test_mark_state_saved_updates_base_version(self) -> None:
        """_mark_state_saved advances base_version to current version."""
        agg = DummyAggregate(make_id())
        agg.increment(1)
        agg.increment(1)
        assert agg.base_version == 0
        agg._mark_state_saved()
        assert agg.base_version == 2
