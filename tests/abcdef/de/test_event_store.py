"""Tests for EventStore abstraction via an in-memory implementation."""

import datetime

from abcdef.de import EventSourcedDomainEvent, EventStore
from abcdef.in_memory import InMemoryEventStore
from tests.abcdef.conftest import make_id

_TS = datetime.datetime(2024, 1, 1, tzinfo=datetime.UTC)


class DummyEvent(EventSourcedDomainEvent):
    """Minimal EventSourcedDomainEvent for event store testing."""

    event_type = "dummy_event"
    value: str

    def __init__(self, value: str, aggregate_id: str = "agg-1") -> None:
        """Initialise with a value and optional aggregate_id."""
        super().__init__(occurred_at=_TS, aggregate_id=aggregate_id)
        object.__setattr__(self, "value", value)


def _evt(value: str) -> DummyEvent:
    """Create a DummyEvent for convenience."""
    return DummyEvent(value=value)


def _val(event: EventSourcedDomainEvent) -> str:
    """Extract value from a DummyEvent, narrowing the type."""
    assert isinstance(event, DummyEvent)
    return event.value


class TestEventStoreMarker:
    """Tests for EventStore architecture marker."""

    def test_event_store_has_de_type_marker(self) -> None:
        """EventStore is marked with __de_type__ = 'event_store'."""
        assert EventStore.__de_type__ == "event_store"  # type: ignore[attr-defined]

    def test_event_store_does_not_have_repository_marker(self) -> None:
        """EventStore must not be marked as a DDD repository."""
        assert getattr(EventStore, "__ddd_type__", None) != "repository"


class TestEventStore:
    """Tests for EventStore abstraction."""

    def test_append_and_retrieve_events(self) -> None:
        """Events appended for an aggregate can be retrieved."""
        store = InMemoryEventStore()
        agg_id = make_id()
        events = [_evt("a"), _evt("b")]

        store.append_events(agg_id, events)
        result = store.get_events(agg_id)

        assert len(result) == 2
        assert _val(result[0]) == "a"
        assert _val(result[1]) == "b"

    def test_get_events_unknown_aggregate_returns_empty(self) -> None:
        """Retrieving events for an unknown aggregate returns an empty list."""
        store = InMemoryEventStore()
        result = store.get_events(make_id())
        assert result == []

    def test_append_multiple_batches(self) -> None:
        """Multiple append calls accumulate events in order."""
        store = InMemoryEventStore()
        agg_id = make_id()

        store.append_events(agg_id, [_evt("first")])
        store.append_events(agg_id, [_evt("second")])
        result = store.get_events(agg_id)

        assert len(result) == 2
        assert _val(result[0]) == "first"
        assert _val(result[1]) == "second"

    def test_events_isolated_per_aggregate(self) -> None:
        """Events for different aggregates do not bleed into each other."""
        store = InMemoryEventStore()
        id_a = make_id()
        id_b = make_id()

        store.append_events(id_a, [_evt("for-a")])
        store.append_events(id_b, [_evt("for-b")])

        assert len(store.get_events(id_a)) == 1
        assert _val(store.get_events(id_a)[0]) == "for-a"
        assert len(store.get_events(id_b)) == 1
        assert _val(store.get_events(id_b)[0]) == "for-b"

    def test_get_all_events_returns_everything(self) -> None:
        """get_all_events returns events across all aggregates in append order."""
        store = InMemoryEventStore()
        store.append_events(make_id(), [_evt("first")])
        store.append_events(make_id(), [_evt("second")])

        assert len(store.get_all_events()) == 2

    def test_get_all_events_empty(self) -> None:
        """get_all_events returns empty list when no events exist."""
        store = InMemoryEventStore()
        assert store.get_all_events() == []

    def test_returned_list_is_a_copy(self) -> None:
        """Mutating the returned list does not affect the store."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [_evt("x")])

        result = store.get_events(agg_id)
        result.clear()

        assert len(store.get_events(agg_id)) == 1

    def test_get_events_after_version_returns_events_after_that_version(self) -> None:
        """after_version=2 skips the first 2 events (versions 0 and 1).

        With 3 events stored (versions 0, 1, 2), after_version=2 returns
        only the third event (version 2, i.e. the event whose position
        in the list is index 2).
        """
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [_evt("a"), _evt("b"), _evt("c")])

        result = store.get_events(agg_id, after_version=2)

        assert len(result) == 1
        assert _val(result[0]) == "c"

    def test_get_events_after_version_zero_returns_all(self) -> None:
        """after_version=0 returns all events (no events are skipped)."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [_evt("a"), _evt("b")])

        assert len(store.get_events(agg_id, after_version=0)) == 2

    def test_get_events_after_version_equal_to_event_count_returns_empty(self) -> None:
        """after_version equal to total event count returns empty list.

        With 2 events stored, after_version=2 means "after all stored
        events", so the result is empty.
        """
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [_evt("a"), _evt("b")])

        assert store.get_events(agg_id, after_version=2) == []

    def test_get_events_after_version_none_returns_all(self) -> None:
        """after_version=None behaves identically to omitting the parameter."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [_evt("a"), _evt("b")])

        assert store.get_events(agg_id, after_version=None) == store.get_events(agg_id)
