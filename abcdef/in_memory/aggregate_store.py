"""In-memory implementation of AggregateStore."""

from typing import Any

from abcdef.core import (
    AggregateId,
    AggregateRoot,
    AggregateStore,
    Snapshot,
)


class InMemoryAggregateStore[TId: AggregateId, TEntity: AggregateRoot](
    AggregateStore[TId, TEntity]
):
    """In-memory AggregateStore implementation.

    Stores state records in a plain dict keyed by string representation of the
    aggregate ID's UUID. Only the latest state record per aggregate is retained.
    Suitable for testing and lightweight use cases where persistence is not required.
    """

    def __init__(self) -> None:
        """Initialise the aggregate store with empty storage."""
        self._store: dict[str, Snapshot[Any]] = {}

    def save_snapshot(self, snapshot: Snapshot[Any]) -> None:
        """Save (or overwrite) the latest state record for an aggregate.

        Args:
            snapshot: The state record to persist.
        """
        self._store[str(snapshot.aggregate_id.value)] = snapshot

    def get_latest_snapshot(self, aggregate_id: TId) -> Snapshot[Any] | None:
        """Retrieve the latest state record for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.

        Returns:
            The latest state record if present, None otherwise.
        """
        return self._store.get(str(aggregate_id.value))

    def delete_snapshots(self, aggregate_id: TId) -> None:
        """Delete all state records for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate whose state records should be removed.
        """
        self._store.pop(str(aggregate_id.value), None)
