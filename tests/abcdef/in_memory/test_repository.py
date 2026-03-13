"""Tests for InMemoryRepository."""

from abcdef.in_memory import InMemoryRepository
from tests.abcdef.conftest import make_id
from tests.abcdef.in_memory.fixtures import DummyAggregate


class TestInMemoryRepository:
    """Tests for InMemoryRepository."""

    def test_save_and_retrieve(self) -> None:
        """A saved aggregate can be retrieved by ID."""
        repo = InMemoryRepository()
        agg_id = make_id()
        agg = DummyAggregate(agg_id, "hello")

        repo.save(agg)
        result = repo.get_by_id(agg_id)

        assert result is not None
        assert result.id == agg_id
        assert result.value == "hello"

    def test_get_by_id_unknown_returns_none(self) -> None:
        """Returns None when no aggregate exists for the given ID."""
        repo = InMemoryRepository()
        assert repo.get_by_id(make_id()) is None

    def test_save_overwrites_existing(self) -> None:
        """Saving an aggregate with an existing ID replaces the previous version."""
        repo = InMemoryRepository()
        agg_id = make_id()

        repo.save(DummyAggregate(agg_id, "original"))
        repo.save(DummyAggregate(agg_id, "updated"))

        result = repo.get_by_id(agg_id)
        assert result is not None
        assert result.value == "updated"

    def test_delete_removes_aggregate(self) -> None:
        """Deleting an aggregate makes it unretrievable."""
        repo = InMemoryRepository()
        agg_id = make_id()
        repo.save(DummyAggregate(agg_id, "hello"))

        repo.delete(agg_id)

        assert repo.get_by_id(agg_id) is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        """Deleting an unknown aggregate silently does nothing."""
        repo = InMemoryRepository()
        repo.delete(make_id())

    def test_find_all_empty(self) -> None:
        """Returns an empty list when no aggregates have been saved."""
        repo = InMemoryRepository()
        assert repo.find_all() == []

    def test_find_all_returns_all_aggregates(self) -> None:
        """Returns all saved aggregates."""
        repo = InMemoryRepository()
        agg1 = DummyAggregate(make_id(), "one")
        agg2 = DummyAggregate(make_id(), "two")
        agg3 = DummyAggregate(make_id(), "three")

        repo.save(agg1)
        repo.save(agg2)
        repo.save(agg3)

        result = repo.find_all()
        assert len(result) == 3
        assert agg1 in result
        assert agg2 in result
        assert agg3 in result

    def test_find_all_excludes_deleted(self) -> None:
        """Deleted aggregates do not appear in find_all."""
        repo = InMemoryRepository()
        agg1 = DummyAggregate(make_id(), "one")
        agg2 = DummyAggregate(make_id(), "two")

        repo.save(agg1)
        repo.save(agg2)
        repo.delete(agg1.id)

        result = repo.find_all()
        assert len(result) == 1
        assert agg2 in result

    def test_aggregates_isolated_by_id(self) -> None:
        """Different aggregate IDs do not interfere with each other."""
        repo = InMemoryRepository()
        agg_a = DummyAggregate(make_id(), "alpha")
        agg_b = DummyAggregate(make_id(), "beta")
        repo.save(agg_a)
        repo.save(agg_b)

        result_a = repo.get_by_id(agg_a.id)
        result_b = repo.get_by_id(agg_b.id)
        assert result_a is not None
        assert result_b is not None
        assert result_a.value == "alpha"
        assert result_b.value == "beta"
