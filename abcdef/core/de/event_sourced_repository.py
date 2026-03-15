"""Event-sourced repository with state persistence strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..d import AggregateId
from ..d.repository import Repository
from .aggregate_store import AggregateRecord, AggregateStore
from .event_sourced_aggregate import EventSourcedAggregate

if TYPE_CHECKING:
    from ..c.message_bus import EventBus
    from .domain_event import DomainEvent
    from .event import Event
    from .event_store import EventStore


class EventSourcedRepository[TId: AggregateId, TEntity: EventSourcedAggregate](
    Repository[TId, TEntity]
):
    """Repository implementing event sourcing with state persistence optimisation.

    Responsibilities:
    - Persisting aggregates via the event store (events) and aggregate store
      (version records and optional state snapshots)
    - Managing state persistence strategy (when to populate state on the record)
    - Orchestrating event replay (full or delta from a state snapshot)
    - Defining how to reconstruct aggregates from events
    - Publishing committed events to the event bus after each successful save

    The event store handles appending events (HOW to persist events).
    The aggregate store handles version records (HOW to track versions and state).
    This repository handles WHEN/WHETHER to populate state and replay logic.

    Optimistic concurrency is enforced via the aggregate store: the pre-commit
    version is passed as ``expected_version`` on every save. If another writer
    has already committed, ``VersionConflictError`` is raised.
    """

    def __init__(
        self,
        event_store: EventStore[TId, TEntity],
        aggregate_store: AggregateStore[TId, TEntity],
        event_bus: EventBus[Event],
        snapshot_threshold: int = 10,
    ) -> None:
        """Initialise the event-sourced repository.

        Args:
            event_store: The store for persisting events (append-only).
            aggregate_store: The store for persisting version records.
            event_bus: The bus to publish committed events to after each save.
            snapshot_threshold: Capture state every N events (default: 10).
        """
        self._event_store = event_store
        self._aggregate_store = aggregate_store
        self._event_bus = event_bus
        self._snapshot_threshold = snapshot_threshold

    def save(self, aggregate: TEntity) -> None:
        """Save an aggregate by persisting its uncommitted events.

        Strategy:
        1. Append events to the event store
        2. Write an aggregate record with the pre-commit version as
           expected_version, enforcing optimistic concurrency
        3. Populate state on the record only if the delta reached the threshold
        4. Publish all committed events to the event bus

        Events are published only after the aggregate store write succeeds,
        ensuring no partial publishes on a failed commit.

        Raises:
            VersionConflictError: If another writer committed a record for this
                aggregate since it was last loaded. The caller must reload and retry.

        Args:
            aggregate: The aggregate to persist.
        """
        events = aggregate._get_uncommitted_events()
        if not events:
            return

        aggregate_id: TId = aggregate.id  # type: ignore[assignment]
        expected_version = aggregate.version - len(events)

        self._event_store.append_events(aggregate_id, events)
        aggregate._mark_events_as_committed()

        delta = aggregate.version - aggregate.base_version
        if delta >= self._snapshot_threshold:
            state = aggregate.create_state()
            record: AggregateRecord = AggregateRecord(
                aggregate_id=aggregate.id,
                event_version=aggregate.version,
                state=state,
            )
            aggregate._mark_state_saved()
        else:
            record = AggregateRecord(
                aggregate_id=aggregate.id,
                event_version=aggregate.version,
            )

        self._aggregate_store.save(record, expected_version=expected_version)

        for event in events:
            self._event_bus.publish(event)

    def get_by_id(self, aggregate_id: TId) -> TEntity | None:
        """Load an aggregate, using a state snapshot if available.

        Strategy:
        1. Check if a record exists
        2. If the record carries state, load it and replay only delta events
        3. Otherwise replay all events from the event store

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The reconstructed aggregate, or None if no events exist.
        """
        record = self._aggregate_store.get(aggregate_id)

        if record is not None and record.state is not None:
            aggregate = self._create_from_state(
                aggregate_id, record.state, record.event_version
            )
            aggregate._load_from_history(
                self._event_store.get_events(
                    aggregate_id, from_version=record.event_version
                )
            )
            return aggregate

        events = self._event_store.get_events(aggregate_id)
        if not events:
            return None

        return self.build_from_events(aggregate_id, events)

    def delete(self, aggregate_id: TId) -> None:
        """Delete is not supported in pure event sourcing.

        In event sourcing, deletion is typically handled via a DeletedEvent.
        Subclasses can override if they need soft-delete support.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        raise NotImplementedError(
            "Pure event sourcing doesn't support deletion. Use a DeletedEvent instead."
        )

    def find_all(self) -> list[TEntity]:
        """Not supported on event-sourced repositories.

        ``find_all()`` requires iterating all aggregates, which is not possible
        directly from an append-only event store without rebuilding every aggregate
        from its full event history. This is impractical at scale and is deliberately
        not implemented here.

        To query all aggregates, use a projection: subscribe to domain events and
        maintain a read model that can be queried efficiently.

        Raises:
            NotImplementedError: Always. This method is intentionally unsupported.
        """
        raise NotImplementedError(
            "find_all() is not supported on event-sourced repositories. "
            "Use a projection to maintain a queryable read model."
        )

    def build_from_events(
        self, aggregate_id: TId, events: list[DomainEvent]
    ) -> TEntity:
        """Reconstruct an aggregate from its full event history.

        Subclasses MUST implement this. The typical implementation creates a
        fresh aggregate instance and calls _load_from_history(events).

        Args:
            aggregate_id: The ID of the aggregate.
            events: All events in chronological order.

        Returns:
            The reconstructed aggregate.
        """
        raise NotImplementedError("Subclasses must implement build_from_events().")

    def _create_from_state(
        self, aggregate_id: TId, state: object, version: int
    ) -> TEntity:
        """Reconstruct an aggregate from a persisted state snapshot.

        Subclasses MUST implement this when snapshot reconstruction is required.
        Typically a one-liner delegating to the concrete aggregate's from_state().

        Example::

            def _create_from_state(self, aggregate_id, state, version):
                return MyAggregate.from_state(aggregate_id, state, version)

        Args:
            aggregate_id: The identity of the aggregate.
            state: The state snapshot to restore from.
            version: The event version at which the state was captured.

        Returns:
            The reconstructed aggregate.
        """
        raise NotImplementedError(
            "Snapshot reconstruction enabled but _create_from_state() not implemented. "
            "Override in subclass if using state snapshots."
        )
