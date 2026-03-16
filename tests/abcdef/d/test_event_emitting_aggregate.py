"""Tests for EventEmittingAggregate."""

import datetime

from abcdef.d import DomainEvent, EventEmittingAggregate
from tests.abcdef.conftest import make_id

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TS = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)


class ThingHappened(DomainEvent):
    """Minimal concrete DomainEvent for testing."""

    event_type = "thing_happened"

    def __init__(self) -> None:
        """Initialise."""
        super().__init__(occurred_at=_TS)


class AnotherThingHappened(DomainEvent):
    """Second minimal concrete DomainEvent for testing."""

    event_type = "another_thing_happened"

    def __init__(self) -> None:
        """Initialise."""
        super().__init__(occurred_at=_TS)


class ConcreteEmitter(EventEmittingAggregate[DomainEvent]):
    """Minimal concrete EventEmittingAggregate for testing."""

    def do_something(self) -> None:
        """Emit a ThingHappened event."""
        self._emit_event(ThingHappened())

    def do_another_thing(self) -> None:
        """Emit an AnotherThingHappened event."""
        self._emit_event(AnotherThingHappened())


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestEventEmittingAggregate:
    """Tests for EventEmittingAggregate."""

    def test_no_pending_events_on_construction(self) -> None:
        """A freshly constructed aggregate has no pending events."""
        agg = ConcreteEmitter(make_id())
        assert agg._get_uncommitted_events() == []

    def test_emit_event_records_event(self) -> None:
        """_emit_event adds the event to the pending list."""
        agg = ConcreteEmitter(make_id())
        agg.do_something()
        events = agg._get_uncommitted_events()
        assert len(events) == 1
        assert isinstance(events[0], ThingHappened)

    def test_emit_multiple_events_records_all(self) -> None:
        """Multiple emitted events are all recorded in order."""
        agg = ConcreteEmitter(make_id())
        agg.do_something()
        agg.do_another_thing()
        events = agg._get_uncommitted_events()
        assert len(events) == 2
        assert isinstance(events[0], ThingHappened)
        assert isinstance(events[1], AnotherThingHappened)

    def test_get_uncommitted_events_returns_copy(self) -> None:
        """_get_uncommitted_events returns a copy, not the internal list."""
        agg = ConcreteEmitter(make_id())
        agg.do_something()
        events = agg._get_uncommitted_events()
        events.clear()
        assert len(agg._get_uncommitted_events()) == 1

    def test_mark_events_as_committed_clears_pending(self) -> None:
        """_mark_events_as_committed empties the pending event list."""
        agg = ConcreteEmitter(make_id())
        agg.do_something()
        agg._mark_events_as_committed()
        assert agg._get_uncommitted_events() == []

    def test_emit_after_commit_records_new_events(self) -> None:
        """Events emitted after a commit are tracked independently."""
        agg = ConcreteEmitter(make_id())
        agg.do_something()
        agg._mark_events_as_committed()
        agg.do_another_thing()
        events = agg._get_uncommitted_events()
        assert len(events) == 1
        assert isinstance(events[0], AnotherThingHappened)

    def test_id_is_accessible(self) -> None:
        """The aggregate id passed at construction is accessible via .id."""
        agg_id = make_id()
        agg = ConcreteEmitter(agg_id)
        assert agg.id is agg_id

    def test_equality_by_id(self) -> None:
        """Two aggregates with the same id are equal."""
        agg_id = make_id()
        assert ConcreteEmitter(agg_id) == ConcreteEmitter(agg_id)

    def test_inequality_by_id(self) -> None:
        """Two aggregates with different ids are not equal."""
        assert ConcreteEmitter(make_id()) != ConcreteEmitter(make_id())

    def test_is_instantiable_directly(self) -> None:
        """EventEmittingAggregate has no abstract methods.

        Subclasses need no mandatory overrides to be instantiable.
        """
        agg = ConcreteEmitter(make_id())
        assert agg is not None

    def test_mark_committed_is_idempotent_on_empty_list(self) -> None:
        """Calling _mark_events_as_committed with no events is a no-op."""
        agg = ConcreteEmitter(make_id())
        agg._mark_events_as_committed()
        assert agg._get_uncommitted_events() == []

    def test_two_instances_have_independent_event_lists(self) -> None:
        """Pending events on one instance do not affect another."""
        a = ConcreteEmitter(make_id())
        b = ConcreteEmitter(make_id())
        a.do_something()
        assert b._get_uncommitted_events() == []


class TestEventEmittingAggregateIsNotAbstract:
    """EventEmittingAggregate imposes no abstract methods on subclasses."""

    def test_subclass_with_no_overrides_is_valid(self) -> None:
        """A subclass that overrides nothing is still instantiable."""

        class MinimalAggregate(EventEmittingAggregate[DomainEvent]):
            pass

        agg = MinimalAggregate(make_id())
        assert agg._get_uncommitted_events() == []
