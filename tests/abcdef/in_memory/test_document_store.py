"""Tests for InMemoryDocumentStore."""

from abcdef.c import Document
from abcdef.in_memory import InMemoryDocumentStore


class UserDocument(Document):
    """Dummy document for testing."""

    def __init__(self, user_id: str, name: str) -> None:
        """Initialise with a user_id and name."""
        self.user_id = user_id
        self.name = name


class TestInMemoryDocumentStore:
    """Tests for InMemoryDocumentStore."""

    def test_save_and_retrieve(self) -> None:
        """A saved document can be retrieved by key."""
        store = InMemoryDocumentStore()
        store.save("u1", UserDocument("u1", "Alice"))

        result = store.get("u1")

        assert result is not None
        assert result.name == "Alice"

    def test_get_unknown_returns_none(self) -> None:
        """Returns None when no document exists for the given key."""
        store = InMemoryDocumentStore()
        assert store.get("missing") is None

    def test_save_replaces_existing(self) -> None:
        """Saving a document with an existing key replaces the previous version."""
        store = InMemoryDocumentStore()
        store.save("u1", UserDocument("u1", "Alice"))
        store.save("u1", UserDocument("u1", "Alicia"))

        result = store.get("u1")
        assert result is not None
        assert result.name == "Alicia"

    def test_delete_removes_document(self) -> None:
        """Deleting a document makes it unretrievable."""
        store = InMemoryDocumentStore()
        store.save("u1", UserDocument("u1", "Alice"))

        store.delete("u1")

        assert store.get("u1") is None

    def test_delete_nonexistent_does_not_raise(self) -> None:
        """Deleting an unknown key silently does nothing."""
        store = InMemoryDocumentStore()
        store.delete("missing")

    def test_find_all_empty(self) -> None:
        """Returns an empty list when no documents have been saved."""
        store = InMemoryDocumentStore()
        assert store.find_all() == []

    def test_find_all_returns_all_documents(self) -> None:
        """Returns all saved documents."""
        store = InMemoryDocumentStore()
        doc1 = UserDocument("u1", "Alice")
        doc2 = UserDocument("u2", "Bob")
        doc3 = UserDocument("u3", "Carol")
        store.save("u1", doc1)
        store.save("u2", doc2)
        store.save("u3", doc3)

        result = store.find_all()

        assert len(result) == 3
        assert doc1 in result
        assert doc2 in result
        assert doc3 in result

    def test_find_all_excludes_deleted(self) -> None:
        """Deleted documents do not appear in find_all."""
        store = InMemoryDocumentStore()
        doc1 = UserDocument("u1", "Alice")
        doc2 = UserDocument("u2", "Bob")
        store.save("u1", doc1)
        store.save("u2", doc2)

        store.delete("u1")

        result = store.find_all()
        assert len(result) == 1
        assert doc2 in result

    def test_documents_isolated_by_key(self) -> None:
        """Different keys do not interfere with each other."""
        store = InMemoryDocumentStore()
        store.save("u1", UserDocument("u1", "Alice"))
        store.save("u2", UserDocument("u2", "Bob"))

        assert store.get("u1") is not None
        assert store.get("u2") is not None
        assert store.get("u1").name == "Alice"  # type: ignore[union-attr]
        assert store.get("u2").name == "Bob"  # type: ignore[union-attr]
