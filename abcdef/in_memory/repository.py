"""In-memory implementation of Repository."""

from copy import deepcopy

from abcdef.d import AggregateId, AggregateRoot, Repository


class InMemoryRepository[TId: AggregateId, TAggregate: AggregateRoot](
    Repository[TId, TAggregate]
):
    """In-memory Repository implementation.

    Generic dict-backed repository suitable for testing and lightweight use cases where
    persistence is not required. Keyed by string representation of the aggregate ID.

    Snapshots on every save and load: the store holds deep copies of aggregates, so
    post-save mutations to the original do not affect the stored version, and
    post-load mutations to the returned instance do not affect the store.

    Subclasses are not required -- this class is fully concrete and can be instantiated
    directly or subclassed to add domain-specific query methods.
    """

    def __init__(self) -> None:
        """Initialise the repository with empty storage."""
        self._store: dict[str, TAggregate] = {}

    def save(self, aggregate: TAggregate) -> None:
        """Save a deep-copy snapshot of the aggregate (insert or update).

        Args:
            aggregate: The aggregate to persist.
        """
        self._store[str(aggregate.id)] = deepcopy(aggregate)

    def get_by_id(self, aggregate_id: TId) -> TAggregate | None:
        """Load an aggregate by its ID.

        Returns a deep copy so post-load mutations do not affect the store.

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            A copy of the aggregate if found, None otherwise.
        """
        stored = self._store.get(str(aggregate_id))
        return deepcopy(stored) if stored is not None else None

    def delete(self, aggregate_id: TId) -> None:
        """Delete an aggregate by its ID.

        Silently does nothing if the aggregate does not exist.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        self._store.pop(str(aggregate_id), None)

    def find_all(self) -> list[TAggregate]:
        """Return deep-copy snapshots of all aggregates.

        Returns:
            Independent copies of all stored aggregates, in insertion order.
        """
        return [deepcopy(v) for v in self._store.values()]
