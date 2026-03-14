"""In-memory implementation of DocumentStore."""

from abcdef.core import Document, DocumentStore


class InMemoryDocumentStore[TDocument: Document](DocumentStore[TDocument]):
    """In-memory DocumentStore implementation.

    Dict-backed store keyed by plain string key. Suitable for testing
    and lightweight use cases where persistence is not required.
    """

    def __init__(self) -> None:
        """Initialise the document store with empty storage."""
        self._store: dict[str, TDocument] = {}

    def save(self, key: str, document: TDocument) -> None:
        """Persist a document (insert or replace).

        Args:
            key: The string key for this document.
            document: The document to persist.
        """
        self._store[key] = document

    def get(self, key: str) -> TDocument | None:
        """Retrieve a document by its key.

        Args:
            key: The string key of the document to retrieve.

        Returns:
            The document if found, None otherwise.
        """
        return self._store.get(key)

    def delete(self, key: str) -> None:
        """Delete a document by its key.

        Silently does nothing if the document does not exist.

        Args:
            key: The string key of the document to delete.
        """
        self._store.pop(key, None)

    def find_all(self) -> list[TDocument]:
        """Retrieve all documents in the store.

        Returns:
            List of all documents in insertion order.
        """
        return list(self._store.values())
