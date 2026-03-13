"""Aggregate Store abstraction for snapshot persistence."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from ..d import AggregateId, AggregateRoot
from .event_sourced_aggregate import AggregateState


@dataclass
class Snapshot[TState: AggregateState]:
    """A point-in-time capture of an aggregate's state.

    Generic over TState so callers that know the concrete state type retain
    full type safety without a cast. Storage layers that don't care about
    the concrete state type can use ``Snapshot[AggregateState]``.

    Attributes:
        aggregate_id: Identity of the aggregate this record belongs to.
        event_version: Index of the last event included in this record.
        state: The aggregate state at ``event_version``.
        timestamp: Optional wall-clock time when the record was created.
    """

    aggregate_id: AggregateId
    event_version: int
    state: TState
    timestamp: float | None = None


class AggregateStore[TId: AggregateId, TEntity: AggregateRoot](ABC):
    """Base interface for aggregate stores.

    An AggregateStore is responsible for persisting aggregate snapshots.
    It abstracts the storage mechanism (in-memory, database, file, etc.).

    Snapshots are point-in-time captures of aggregate state for performance
    optimisation. They include metadata (event version, timestamp) to determine
    delta events.

    Concrete implementations decide HOW to store snapshots
    (SQLite, PostgreSQL, etc.).
    """

    @abstractmethod
    def save_snapshot(self, snapshot: Snapshot[Any]) -> None:
        """Save a snapshot for an aggregate.

        Args:
            snapshot: The snapshot containing state and metadata.
        """
        pass

    @abstractmethod
    def get_latest_snapshot(self, aggregate_id: TId) -> Snapshot[Any] | None:
        """Retrieve the latest snapshot for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.

        Returns:
            The latest snapshot if available, None otherwise.
        """
        pass

    @abstractmethod
    def delete_snapshots(self, aggregate_id: TId) -> None:
        """Delete all snapshots for an aggregate.

        Used when rebuilding state or cleaning up.

        Args:
            aggregate_id: The ID of the aggregate.
        """
        pass
