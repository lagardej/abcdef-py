"""In-memory implementation of AggregateStore."""

from typing import Any

from abcdef.core import (
    AggregateId,
    AggregateRecord,
    AggregateRoot,
    AggregateStore,
)
from abcdef.core.de.aggregate_store import VersionConflictError


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

    def save(
        self,
        record: AggregateRecord[Any],
        expected_version: int | None = None,
    ) -> None:
        """Save (or overwrite) the record for an aggregate.

        If ``expected_version`` is provided, raises ``VersionConflictError``
        when the stored version does not match. No write occurs on conflict.

        Args:
            record: The record to persist.
            expected_version: Expected current version of the aggregate.
                Pass ``None`` to skip the conflict check.

        Raises:
            VersionConflictError: If ``expected_version`` does not match the
                current stored version for the aggregate.
        """
        if expected_version is not None:
            current = self._store.get(str(record.aggregate_id))
            actual = current.event_version if current is not None else 0
            if actual != expected_version:
                raise VersionConflictError(expected=expected_version, actual=actual)

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
