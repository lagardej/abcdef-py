"""Tests for Repository abstraction."""

from tests.abcdef.conftest import make_id
from tests.abcdef.d.fixtures import DummyAggregate, DummyRepository


class TestRepository:
    """Tests for Repository abstraction."""

    def test_repository_save_and_retrieve(self) -> None:
        """Test that aggregates can be saved and retrieved."""
        repo = DummyRepository()
        agg_id = make_id()
        dummy = DummyAggregate(agg_id, "Alice")

        repo.save(dummy)
        retrieved = repo.get_by_id(agg_id)

        assert retrieved is not None
        assert retrieved.id == agg_id
        assert retrieved.name == "Alice"

    def test_repository_get_nonexistent(self) -> None:
        """Test that retrieving nonexistent aggregate returns None."""
        repo = DummyRepository()
        assert repo.get_by_id(make_id()) is None

    def test_repository_delete(self) -> None:
        """Test that aggregates can be deleted."""
        repo = DummyRepository()
        agg_id = make_id()
        dummy = DummyAggregate(agg_id, "Alice")

        repo.save(dummy)
        assert repo.get_by_id(agg_id) is not None

        repo.delete(agg_id)
        assert repo.get_by_id(agg_id) is None

    def test_repository_delete_nonexistent(self) -> None:
        """Test that deleting nonexistent aggregate doesn't raise."""
        repo = DummyRepository()
        repo.delete(make_id())

    def test_repository_find_all_empty(self) -> None:
        """Test that find_all returns empty list when no aggregates exist."""
        repo = DummyRepository()
        assert repo.find_all() == []

    def test_repository_find_all(self) -> None:
        """Test that find_all returns all aggregates."""
        repo = DummyRepository()
        dummy1 = DummyAggregate(make_id(), "Alice")
        dummy2 = DummyAggregate(make_id(), "Bob")
        dummy3 = DummyAggregate(make_id(), "Carol")

        repo.save(dummy1)
        repo.save(dummy2)
        repo.save(dummy3)

        result = repo.find_all()

        assert len(result) == 3
        assert dummy1 in result
        assert dummy2 in result
        assert dummy3 in result

    def test_repository_update(self) -> None:
        """Test that aggregates can be updated."""
        repo = DummyRepository()
        agg_id = make_id()
        dummy = DummyAggregate(agg_id, "Alice")

        repo.save(dummy)

        dummy.name = "Alicia"
        repo.save(dummy)

        retrieved = repo.get_by_id(agg_id)
        assert retrieved is not None
        assert retrieved.name == "Alicia"
