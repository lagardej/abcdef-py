"""Aggregate Store abstraction for aggregate version tracking and snapshots."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..d import AggregateId, AggregateRoot
from .event_sourced_aggregate import AggregateState


class VersionConflictError(Exception):
    """Raised when a save is attempted with a stale expected version.

    Indicates that another writer has already committed a newer record for
    this aggregate since the caller last loaded it. The caller must reload
    the aggregate and retry.
    """

    def __init__(self, expected: int, actual: int) -> None:
        """Initialise with the expected and actual versions.

        Args:
            expected: The version the caller expected to find.
            actual: The version currently stored.
        """
        super().__init__(
            f"Version conflict: expected {expected}, but store is at {actual}."
        )
        self.expected = expected
        self.actual = actual


@dataclass
class AggregateRecord[TState: AggregateState]:
    """A version record for an aggregate, optionally carrying a state snapshot.

    Every save writes an AggregateRecord. The ``state`` field is populated only
    when the snapshot threshold is reached; otherwise it is ``None``. This makes
    AggregateStore the authoritative registry of aggregate identity and current
    version, regardless of whether a snapshot has been taken.

    Generic over TState so callers that know the concrete state type retain
    full type safety without a cast. Storage layers that don't care about
    the concrete state type can use ``AggregateRecord[AggregateState]``.

    Attributes:
        aggregate_id: Identity of the aggregate this record belongs to.
        event_version: The aggregate's version at the time this record was written.
        state: The aggregate state at ``event_version``, or ``None`` if no
            snapshot was taken at this version.
        timestamp: Optional wall-clock time when the record was written.
    """

    aggregate_id: AggregateId
    event_version: int
    state: TState | None = field(default=None)
    timestamp: float | None = field(default=None)


class AggregateStore[TId: AggregateId, TEntity: AggregateRoot](ABC):
    """Base interface for aggregate stores.

    An AggregateStore tracks the current version of every aggregate and
    optionally caches state snapshots for replay optimisation.

    A record is written on every save. The snapshot threshold in the repository
    controls whether ``state`` is populated -- not whether the record is written.

    Optimistic concurrency is enforced here: ``save`` accepts an
    ``expected_version`` parameter. If the stored version does not match,
    ``VersionConflictError`` is raised and no write occurs.

    Concrete implementations decide HOW to persist records
    (SQLite, PostgreSQL, etc.).
    """

    @abstractmethod
    def save(
        self,
        record: AggregateRecord[Any],
        expected_version: int | None = None,
    ) -> None:
        """Save (or overwrite) the record for an aggregate.

        Optimistic concurrency contract:
        - If ``expected_version`` is ``None``, the save proceeds unconditionally.
        - If ``expected_version`` is an integer, the store checks that the current
          record's ``event_version`` equals ``expected_version``. If no record
          exists, the current version is treated as 0. On mismatch,
          ``VersionConflictError`` is raised and no write occurs.

        Args:
            record: The record to persist.
            expected_version: The version the caller expects to find in the store.
                Pass ``None`` to skip the conflict check.

        Raises:
            VersionConflictError: If ``expected_version`` is provided and does not
                match the current stored version for the aggregate.
        """
        pass

    @abstractmethod
    def get(self, aggregate_id: TId) -> AggregateRecord[Any] | None:
        """Retrieve the current record for an aggregate.

        Args:
            aggregate_id: The ID of the aggregate.

        Returns:
            The record if present, None otherwise.
        """
        pass

    @abstractmethod
    def delete(self, aggregate_id: TId) -> None:
        """Delete the record for an aggregate.

        Used when rebuilding state or cleaning up.

        Args:
            aggregate_id: The ID of the aggregate.
        """
        pass
