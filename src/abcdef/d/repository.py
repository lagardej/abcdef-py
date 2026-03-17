"""Repository abstraction for persistence."""

from abc import ABC, abstractmethod

from . import markers
from .aggregate import AggregateId, AggregateRoot


@markers.repository
class Repository[TId: AggregateId, TEntity: AggregateRoot](ABC):
    """Base interface for repositories.

    A Repository abstracts persistence, making aggregates appear to be in memory.
    It provides methods to load and save aggregates by their ID.

    Repositories are responsible for:
    - Loading aggregates from storage (reconstructing state)
    - Saving new aggregates
    - Updating existing aggregates
    - Deleting aggregates

    The actual persistence mechanism (database, file, etc.) is hidden from
    the domain layer.
    """

    @abstractmethod
    def save(self, aggregate: TEntity) -> None:
        """Save an aggregate (insert or update).

        Args:
            aggregate: The aggregate to persist.
        """
        pass

    @abstractmethod
    def get_by_id(self, aggregate_id: TId) -> TEntity | None:
        """Load an aggregate by its ID.

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The aggregate if found, None otherwise.
        """
        pass

    @abstractmethod
    def delete(self, aggregate_id: TId) -> None:
        """Delete an aggregate by its ID.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        pass

    @abstractmethod
    def find_all(self) -> list[TEntity]:
        """Load all aggregates.

        Returns:
            List of all aggregates in storage.
        """
        pass
