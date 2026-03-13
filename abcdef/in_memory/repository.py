"""In-memory implementation of Repository."""

from abcdef.core import AggregateId, AggregateRoot, Repository


class InMemoryRepository[TId: AggregateId, TAggregate: AggregateRoot](
    Repository[TId, TAggregate]
):
    """In-memory Repository implementation.

    Generic dict-backed repository suitable for testing and lightweight use cases
    where persistence is not required. Keyed by string representation of the
    aggregate ID's UUID.

    Subclasses are not required — this class is fully concrete and can be
    instantiated directly or subclassed to add domain-specific query methods.
    """

    def __init__(self) -> None:
        """Initialise the repository with empty storage."""
        self._store: dict[str, TAggregate] = {}

    def save(self, aggregate: TAggregate) -> None:
        """Save an aggregate (insert or update).

        Args:
            aggregate: The aggregate to persist.
        """
        self._store[str(aggregate.id.value)] = aggregate

    def get_by_id(self, aggregate_id: TId) -> TAggregate | None:
        """Load an aggregate by its ID.

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The aggregate if found, None otherwise.
        """
        return self._store.get(str(aggregate_id.value))

    def delete(self, aggregate_id: TId) -> None:
        """Delete an aggregate by its ID.

        Silently does nothing if the aggregate does not exist.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        self._store.pop(str(aggregate_id.value), None)

    def find_all(self) -> list[TAggregate]:
        """Return all aggregates in the repository.

        Returns:
            List of all stored aggregates, in insertion order.
        """
        return list(self._store.values())
