"""Tests for EventStore abstraction via an in-memory implementation."""

from abcdef.core import EventStore
from abcdef.in_memory import InMemoryEventStore
from tests.abcdef.conftest import make_id


class DummyEvent:
    """Dummy event for testing."""

    def __init__(self, value: str) -> None:
        """Initialise with a value."""
        self.value = value


class TestEventStoreMarker:
    """Tests for EventStore architecture marker."""

    def test_event_store_has_es_type_marker(self) -> None:
        """EventStore is marked with __es_type__ = 'event_store'."""
        assert EventStore.__es_type__ == "event_store"  # type: ignore[attr-defined]

    def test_event_store_does_not_have_repository_marker(self) -> None:
        """EventStore must not be marked as a DDD repository."""
        assert getattr(EventStore, "__ddd_type__", None) != "repository"


class TestEventStore:
    """Tests for EventStore abstraction."""

    def test_append_and_retrieve_events(self) -> None:
        """Events appended for an aggregate can be retrieved."""
        store = InMemoryEventStore()
        agg_id = make_id()
        events = [DummyEvent("a"), DummyEvent("b")]

        store.append_events(agg_id, events)
        result = store.get_events(agg_id)

        assert len(result) == 2
        assert result[0].value == "a"
        assert result[1].value == "b"

    def test_get_events_unknown_aggregate_returns_empty(self) -> None:
        """Retrieving events for an unknown aggregate returns an empty list."""
        store = InMemoryEventStore()
        result = store.get_events(make_id())
        assert result == []

    def test_append_multiple_batches(self) -> None:
        """Multiple append calls accumulate events in order."""
        store = InMemoryEventStore()
        agg_id = make_id()

        store.append_events(agg_id, [DummyEvent("first")])
        store.append_events(agg_id, [DummyEvent("second")])
        result = store.get_events(agg_id)

        assert len(result) == 2
        assert result[0].value == "first"
        assert result[1].value == "second"

    def test_events_isolated_per_aggregate(self) -> None:
        """Events for different aggregates do not bleed into each other."""
        store = InMemoryEventStore()
        id_a = make_id()
        id_b = make_id()

        store.append_events(id_a, [DummyEvent("for-a")])
        store.append_events(id_b, [DummyEvent("for-b")])

        assert len(store.get_events(id_a)) == 1
        assert store.get_events(id_a)[0].value == "for-a"
        assert len(store.get_events(id_b)) == 1
        assert store.get_events(id_b)[0].value == "for-b"

    def test_get_all_events_returns_everything(self) -> None:
        """get_all_events returns events across all aggregates in append order."""
        store = InMemoryEventStore()
        store.append_events(make_id(), [DummyEvent("first")])
        store.append_events(make_id(), [DummyEvent("second")])

        all_events = store.get_all_events()
        assert len(all_events) == 2

    def test_get_all_events_empty(self) -> None:
        """get_all_events returns empty list when no events exist."""
        store = InMemoryEventStore()
        assert store.get_all_events() == []

    def test_returned_list_is_a_copy(self) -> None:
        """Mutating the returned list does not affect the store."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [DummyEvent("x")])

        result = store.get_events(agg_id)
        result.clear()

        assert len(store.get_events(agg_id)) == 1

    def test_get_events_from_version_returns_events_from_that_index(self) -> None:
        """from_version skips events before the given version."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [DummyEvent("a"), DummyEvent("b"), DummyEvent("c")])

        result = store.get_events(agg_id, from_version=2)

        assert len(result) == 1
        assert result[0].value == "c"

    def test_get_events_from_version_zero_returns_all(self) -> None:
        """from_version=0 returns all events."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [DummyEvent("a"), DummyEvent("b")])

        result = store.get_events(agg_id, from_version=0)

        assert len(result) == 2

    def test_get_events_from_version_equal_to_length_returns_empty(self) -> None:
        """from_version equal to total event count returns empty list."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [DummyEvent("a"), DummyEvent("b")])

        result = store.get_events(agg_id, from_version=2)

        assert result == []

    def test_get_events_from_version_none_returns_all(self) -> None:
        """from_version=None behaves identically to omitting the parameter."""
        store = InMemoryEventStore()
        agg_id = make_id()
        store.append_events(agg_id, [DummyEvent("a"), DummyEvent("b")])

        assert store.get_events(agg_id, from_version=None) == store.get_events(agg_id)
