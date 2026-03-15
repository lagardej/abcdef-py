"""In-memory implementation of AggregateStore."""

from typing import Any

from abcdef.core import (
    AggregateId,
    AggregateRecord,
    AggregateRoot,
    AggregateStore,
)


class InMemoryAggregateStore[TId: AggregateId, TEntity: AggregateRoot](
    AggregateStore[TId, TEntity]
):
    """In-memory AggregateStore implementation.

    Stores aggregate records in a plain dict keyed by string representation of
    the aggregate ID's UUID. Only the latest record per aggregate is retained.
    Suitable for testing and lightweight use cases where persistence is not required.
    """

    def __init__(self) -> None:
        """Initialise the aggregate store with empty storage."""
        self._store: dict[str, AggregateRecord[Any]] = {}

    def save(self, record: AggregateRecord[Any]) -> None:
        """Save (or overwrite) the record for an aggregate.

        Args:
            record: The record to persist.
        """
        self._store[str(record.aggregate_id)] = record

    def get(self, aggregate_id: TId) -> AggregateRecord[Any] | None:
        """Retrieve the current record for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.

        Returns:
            The record if present, None otherwise.
        """
        return self._store.get(str(aggregate_id))

    def delete(self, aggregate_id: TId) -> None:
        """Delete the record for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate whose record should be removed.
        """
        self._store.pop(str(aggregate_id), None)
