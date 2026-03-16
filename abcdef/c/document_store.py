"""DocumentStore abstraction for query-side persistence."""

from abc import ABC, abstractmethod

from . import markers
from .document import Document


@markers.document_store
class DocumentStore[TDocument: Document](ABC):
    """Base interface for document stores.

    A DocumentStore persists and retrieves denormalised read models (documents). It is
    the query-side counterpart to the Repository on the write side.

    Documents are keyed by a plain string key. Implementations are free to use any
    storage backend suited to document-oriented access patterns (in-memory dict, JSON
    files, MongoDB, etc.).

    Each DocumentStore is typed to a single document type.
    """

    @abstractmethod
    def save(self, key: str, document: TDocument) -> None:
        """Persist a document (insert or replace).

        Args:
            key: The string key for this document.
            document: The document to persist.
        """
        pass

    @abstractmethod
    def get(self, key: str) -> TDocument | None:
        """Retrieve a document by its key.

        Args:
            key: The string key of the document to retrieve.

        Returns:
            The document if found, None otherwise.
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Delete a document by its key.

        Silently does nothing if the document does not exist.

        Args:
            key: The string key of the document to delete.
        """
        pass

    @abstractmethod
    def find_all(self) -> list[TDocument]:
        """Retrieve all documents in the store.

        Returns:
            List of all documents in insertion order.
        """
        pass
