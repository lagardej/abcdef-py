"""Event-sourced repository with state persistence strategy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..d import AggregateId
from ..d.repository import Repository
from .aggregate_store import AggregateRecord, AggregateStore
from .event_sourced_aggregate import AggregateRegistry, EventSourcedAggregate

if TYPE_CHECKING:
    from ..c.message_bus import EventBus
    from .event import Event
    from .event_store import EventStore


class EventSourcedRepository[TId: AggregateId, TEntity: EventSourcedAggregate](
    Repository[TId, TEntity]
):
    """Repository implementing event sourcing with state persistence optimisation.

    Responsibilities:
    - Persisting aggregates via the event store (events) and aggregate
      store (version records and optional state snapshots)
    - Managing state persistence strategy (when to populate state on
      the record)
    - Orchestrating event replay (full or delta from a state snapshot)
    - Publishing committed events to the event bus after each successful
      save

    Subclasses MUST declare a non-empty ``aggregate_type`` class variable
    directly on the class. This must match the ``aggregate_type`` declared
    on the aggregate class managed by this repository.

    An ``AggregateRegistry`` must be supplied at construction time. The
    registry is used to resolve aggregate classes by type string during
    rehydration. It is the caller's responsibility to populate the
    registry with all aggregate classes before use.

    The event store handles appending events (HOW to persist events).
    The aggregate store handles version records (HOW to track versions
    and state). This repository handles WHEN/WHETHER to populate state
    and replay logic.

    Optimistic concurrency is enforced via the aggregate store: the
    pre-commit version is passed as ``expected_version`` on every save.
    If another writer has already committed, ``VersionConflictError`` is
    raised.
    """

    aggregate_type: str = ""
    _abstract_repository: bool = False

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Enforce aggregate_type declaration on all concrete subclasses.

        Raises:
            TypeError: If a concrete subclass does not declare a non-empty
                ``aggregate_type`` directly in its own class body.
        """
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("_abstract_repository"):
            return
        if "aggregate_type" not in cls.__dict__ or not cls.__dict__["aggregate_type"]:
            raise TypeError(
                f"{cls.__qualname__} must declare a non-empty "
                f"'aggregate_type' class variable. "
                f"It cannot be inherited from a parent class."
            )

    def __init__(
        self,
        event_store: EventStore[TId, TEntity],
        aggregate_store: AggregateStore[TId, TEntity],
        event_bus: EventBus[Event],
        aggregate_registry: AggregateRegistry,
        snapshot_threshold: int = 10,
    ) -> None:
        """Initialise the event-sourced repository.

        Args:
            event_store: The store for persisting events (append-only).
            aggregate_store: The store for persisting version records.
            event_bus: The bus to publish committed events to after each
                save.
            aggregate_registry: Registry used to resolve aggregate classes
                by aggregate_type string during rehydration.
            snapshot_threshold: Capture state every N events (default: 10).
        """
        self._event_store = event_store
        self._aggregate_store = aggregate_store
        self._event_bus = event_bus
        self._aggregate_registry = aggregate_registry
        self._snapshot_threshold = snapshot_threshold

    def save(self, aggregate: TEntity) -> None:
        """Save an aggregate by persisting its uncommitted events.

        Strategy:
        1. Append events to the event store
        2. Write an aggregate record with the pre-commit version as
           expected_version, enforcing optimistic concurrency
        3. Populate state on the record only if the delta reached the
           threshold
        4. Publish all committed events to the event bus

        Events are published only after the aggregate store write
        succeeds, ensuring no partial publishes on a failed commit.

        Raises:
            VersionConflictError: If another writer committed a record
                for this aggregate since it was last loaded. The caller
                must reload and retry.

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
                aggregate_type=aggregate.aggregate_type,
                event_version=aggregate.version,
                state=state,
            )
            aggregate._mark_state_saved()
        else:
            record = AggregateRecord(
                aggregate_id=aggregate.id,
                aggregate_type=aggregate.aggregate_type,
                event_version=aggregate.version,
            )

        self._aggregate_store.save(record, expected_version=expected_version)

        for event in events:
            self._event_bus.publish(event)

    def get_by_id(self, aggregate_id: TId) -> TEntity | None:
        """Load an aggregate using the two-step rehydration strategy.

        Strategy:
        1. Check the aggregate store for a record (snapshot + version)
        2. Fetch events from the event store from the snapshot version
           (or all events if no snapshot exists)
        3. Reconstruct the aggregate from the snapshot (if present) then
           replay any remaining events

        The aggregate class is resolved from the injected registry using
        the ``aggregate_type`` stored on the record, or from this
        repository's own ``aggregate_type`` when no record exists and
        events must be replayed from scratch.

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The reconstructed aggregate, or None if no events exist.
        """
        record = self._aggregate_store.get(aggregate_id)
        snapshot_version: int | None = (
            record.event_version
            if (record is not None and record.state is not None)
            else None
        )

        events = self._event_store.get_events(
            aggregate_id, from_version=snapshot_version
        )

        if snapshot_version is None and not events:
            return None

        agg_type = record.aggregate_type if record is not None else self.aggregate_type
        cls = self._aggregate_registry.get(agg_type)

        if snapshot_version is not None:
            assert record is not None
            agg = cls.from_state(aggregate_id, record.state, snapshot_version)
        else:
            agg = cls(aggregate_id)

        agg._load_from_history(events)
        return agg  # type: ignore[return-value]

    def delete(self, aggregate_id: TId) -> None:
        """Delete is not supported in pure event sourcing.

        In event sourcing, deletion is typically handled via a
        DeletedEvent. Subclasses can override if they need soft-delete
        support.

        Args:
            aggregate_id: The ID of the aggregate to delete.
        """
        raise NotImplementedError(
            "Pure event sourcing doesn't support deletion. Use a DeletedEvent instead."
        )

    def find_all(self) -> list[TEntity]:
        """Not supported on event-sourced repositories.

        ``find_all()`` requires iterating all aggregates, which is not
        possible directly from an append-only event store without
        rebuilding every aggregate from its full event history. This is
        impractical at scale and is deliberately not implemented here.

        To query all aggregates, use a projection: subscribe to domain
        events and maintain a read model that can be queried efficiently.

        Raises:
            NotImplementedError: Always. This method is intentionally
                unsupported.
        """
        raise NotImplementedError(
            "find_all() is not supported on event-sourced repositories. "
            "Use a projection to maintain a queryable read model."
        )
