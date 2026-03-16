"""Event-sourced repository with state persistence strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..d import AggregateId
from ..d.repository import Repository
from .aggregate_store import AggregateRecord, AggregateStore
from .event_sourced_aggregate import AggregateRegistry, EventSourcedAggregate

if TYPE_CHECKING:
    from ..c.message_bus import EventBus
    from .event_sourced_domain_event import EventSourcedDomainEvent
    from .event_store import EventStore


class EventSourcedRepository[TId: AggregateId, TEntity: EventSourcedAggregate](
    Repository[TId, TEntity]
):
    """Repository implementing event sourcing with state persistence optimisation.

    Responsibilities:
    - Persisting aggregates via the event store (events) and aggregate store (version
      records and optional state snapshots)
    - Managing state persistence strategy (when to populate state on the record)
    - Orchestrating event replay (full or delta from a state snapshot)
    - Publishing committed events to the event bus after each successful save

    An ``AggregateRegistry`` must be supplied at construction time. The registry is
    used to resolve aggregate classes by type string during rehydration. It is the
    caller's responsibility to populate the registry with all aggregate classes before
    use.

    The event store handles appending events (HOW to persist events). The aggregate
    store handles version records (HOW to track versions and state). This repository
    handles WHEN/WHETHER to populate state and replay logic.

    Optimistic concurrency is enforced via the aggregate store: the pre-commit version
    is passed as ``expected_version`` on every save. If another writer has already
    committed, ``VersionConflictError`` is raised before any writes occur.
    """

    def __init__(
        self,
        event_store: EventStore[TId, TEntity],
        aggregate_store: AggregateStore[TId, TEntity],
        event_bus: EventBus[EventSourcedDomainEvent],
        aggregate_registry: AggregateRegistry,
        snapshot_threshold: int = 10,
    ) -> None:
        """Initialise the event-sourced repository.

        Args:
            event_store: The store for persisting events (append-only).
            aggregate_store: The store for persisting version records.
            event_bus: The bus to publish committed events to after each save.
            aggregate_registry: Registry used to resolve aggregate classes by
                aggregate_type string during rehydration.
            snapshot_threshold: Capture state every N events (default: 10).
        """
        self._event_store = event_store
        self._aggregate_store = aggregate_store
        self._event_bus = event_bus
        self._aggregate_registry = aggregate_registry
        self._snapshot_threshold = snapshot_threshold

    def save(self, aggregate: TEntity) -> None:
        """Save an aggregate by persisting its uncommitted events.

        All steps execute in this order:

        1. Check concurrency: write the aggregate record with ``expected_version`` set
           to the pre-emit version. If another writer has already committed,
           ``VersionConflictError`` is raised here and nothing else happens.
        2. Update the aggregate record: write the new version and the state snapshot if
           the delta has reached the threshold. On a successful write, advance
           ``base_version`` on the aggregate if a snapshot was persisted.
        3. Append events to the event store.
        4. Mark events as committed on the aggregate.
        5. Publish all committed events to the event bus.

        **Atomicity warning:** steps 2 and 3 write to two separate stores with no
        distributed transaction between them. If ``append_events`` (step 3) raises
        after ``aggregate_store.save`` (step 2) has already succeeded, the version
        record will be ahead of the event log: the aggregate's version is recorded but
        its events are missing, leaving it unreconstructable via ``get_by_id``.

        This is a fatal storage fault, not a retryable conflict. Recovery requires
        external intervention -- for example, an outbox pattern, a saga, or manual
        reconciliation. The framework does not attempt to compensate automatically.

        Raises:
            VersionConflictError: If another writer committed a record for this
                aggregate since it was last loaded. No writes occur. The caller must
                discard the aggregate, reload, and re-apply the business intent.

        Args:
            aggregate: The aggregate to persist.
        """
        events = aggregate._get_uncommitted_events()
        if not events:
            return

        aggregate_id: TId = aggregate.id  # type: ignore[assignment]
        expected_version = aggregate.version - len(events)
        delta = aggregate.version - aggregate.base_version

        # Step 1 + 2: concurrency check and record write (atomic).
        # VersionConflictError raised here aborts before any other write.
        if delta >= self._snapshot_threshold:
            state = aggregate.create_state()
            record: AggregateRecord = AggregateRecord(
                aggregate_id=aggregate.id,
                aggregate_type=aggregate.aggregate_type,
                event_version=aggregate.version,
                state=state,
            )
        else:
            record = AggregateRecord(
                aggregate_id=aggregate.id,
                aggregate_type=aggregate.aggregate_type,
                event_version=aggregate.version,
            )
        self._aggregate_store.save(record, expected_version=expected_version)

        # Step 2 (cont.): advance base_version now that the snapshot is safely
        # persisted.
        if delta >= self._snapshot_threshold:
            aggregate._mark_state_saved()

        # Step 3: append events to the event store.
        # WARNING: not atomic with step 2 -- see docstring.
        self._event_store.append_events(aggregate_id, events)

        # Step 4: mark events as committed on the aggregate.
        aggregate._mark_events_as_committed()

        # Step 5: publish committed events to the bus.
        for event in events:
            self._event_bus.publish(event)

    def get_by_id(self, aggregate_id: TId) -> TEntity | None:
        """Load an aggregate using the two-step rehydration strategy.

        Strategy:
        1. Check the aggregate store for a record (snapshot + version)
        2. Fetch events from the event store from the snapshot version (or all events
           if no snapshot exists)
        3. Reconstruct the aggregate from the snapshot (if present) then replay any
           remaining events

        A record and its events are always written together. Events without a record
        is a storage fault and must not occur.

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The reconstructed aggregate, or None if neither record nor events exist.

        Raises:
            RuntimeError: If events exist for the aggregate but no aggregate record is
                found. This indicates a storage fault -- record and events must always
                be written together.
        """
        record = self._aggregate_store.get(aggregate_id)
        snapshot_version: int | None = (
            record.event_version
            if (record is not None and record.state is not None)
            else None
        )

        events = self._event_store.get_events(
            aggregate_id, after_version=snapshot_version
        )

        if record is None and not events:
            return None

        if record is None:
            raise RuntimeError(
                f"Events exist for aggregate {aggregate_id} but no aggregate record "
                f"was found. This indicates a storage fault -- record and events must "
                f"always be written together."
            )

        cls = self._aggregate_registry.get(record.aggregate_type)

        if snapshot_version is not None:
            agg = cls.from_state(aggregate_id, record.state, snapshot_version)
        else:
            agg = cls(aggregate_id)

        agg._load_from_history(events)
        return agg  # type: ignore[return-value]

    def delete(self, aggregate_id: TId) -> None:
        """Delete is not supported in pure event sourcing.

        In event sourcing, deletion is typically handled via a DeletedEvent. Subclasses
        can override if they need soft-delete support.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        raise NotImplementedError(
            "Pure event sourcing doesn't support deletion. Use a DeletedEvent instead."
        )

    def find_all(self) -> list[TEntity]:
        """Not supported on event-sourced repositories.

        ``find_all()`` requires iterating all aggregates, which is not possible
        directly from an append-only event store without rebuilding every aggregate from
        its full event history. This is impractical at scale and is deliberately not
        implemented here.

        To query all aggregates, use a projection: subscribe to domain events and
        maintain a read model that can be queried efficiently.

        Raises:
            NotImplementedError: Always. This method is intentionally unsupported.
        """
        raise NotImplementedError(
            "find_all() is not supported on event-sourced repositories. "
            "Use a projection to maintain a queryable read model."
        )
