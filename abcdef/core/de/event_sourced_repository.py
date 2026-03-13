"""Event-sourced repository with state persistence strategy."""

from ..d import AggregateId
from ..d.repository import Repository
from .aggregate_store import AggregateStore, Snapshot
from .event_sourced_aggregate import EventSourcedAggregate
from .event_store import EventStore


class EventSourcedRepository[TId: AggregateId, TEntity: EventSourcedAggregate](
    Repository[TId, TEntity]
):
    """Repository implementing event sourcing with state persistence optimisation.

    Responsibilities:
    - Persisting aggregates via the event store (events) and aggregate store
      (state records)
    - Managing state persistence strategy (when to capture/use state records)
    - Orchestrating event replay (full or delta from a state record)
    - Defining how to reconstruct aggregates from events

    The event store handles appending events (HOW to persist events).
    The aggregate store handles state records (HOW to persist state).
    This repository handles WHEN/WHETHER to use state records and replay logic.
    """

    def __init__(
        self,
        event_store: EventStore[TId, TEntity],
        aggregate_store: AggregateStore[TId, TEntity],
        snapshot_threshold: int = 10,
    ) -> None:
        """Initialise the event-sourced repository.

        Args:
            event_store: The store for persisting events (append-only).
            aggregate_store: The store for persisting state records.
            snapshot_threshold: Persist state every N events (default: 10).
        """
        self._event_store = event_store
        self._aggregate_store = aggregate_store
        self._snapshot_threshold = snapshot_threshold

    def save(self, aggregate: TEntity) -> None:
        """Save an aggregate by persisting its uncommitted events.

        Strategy:
        1. Append events to the event store
        2. Check if state should be persisted (based on event delta)
        3. Capture and save state record if threshold reached

        Args:
            aggregate: The aggregate to persist.
        """
        events = aggregate._get_uncommitted_events()
        if events:
            aggregate_id: TId = aggregate.id  # type: ignore[assignment]
            self._event_store.append_events(aggregate_id, events)
            aggregate._mark_events_as_committed()

            delta = aggregate.version - aggregate.base_version
            if delta >= self._snapshot_threshold:
                state = aggregate.create_state()
                snapshot = Snapshot(
                    aggregate_id=aggregate.id,
                    event_version=aggregate.version,
                    state=state,
                )
                self._aggregate_store.save_snapshot(snapshot)
                aggregate._mark_state_saved()

    def get_by_id(self, aggregate_id: TId) -> TEntity | None:
        """Load an aggregate, using a persisted state record if available.

        Strategy:
        1. Check if a state record exists
        2. If state record exists, load it and replay events after it
        3. If no state record, replay all events from start

        Args:
            aggregate_id: The ID of the aggregate to load.

        Returns:
            The reconstructed aggregate, or None if no events exist.
        """
        snapshot = self._aggregate_store.get_latest_snapshot(aggregate_id)

        if snapshot:
            aggregate = self._create_from_state(
                aggregate_id, snapshot.state, snapshot.event_version
            )
            aggregate._load_from_history(
                self._event_store.get_events(
                    aggregate_id, from_version=snapshot.event_version
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
        """Find all aggregates requires projections or snapshots.

        Returns:
            List of all reconstructed aggregates.
        """
        raise NotImplementedError(
            "find_all() requires projections or rebuilding from all events. "
            "Implement in a subclass or use a projection system."
        )

    def build_from_events(self, aggregate_id: TId, events: list) -> TEntity:
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
        """Reconstruct an aggregate from a persisted state record.

        Subclasses MUST implement this when state persistence is required.
        Typically a one-liner delegating to the concrete aggregate's from_state().

        Example::

            def _create_from_state(self, aggregate_id, state, version):
                return MyAggregate.from_state(aggregate_id, state, version)

        Args:
            aggregate_id: The identity of the aggregate.
            state: The state record to restore from.
            version: The event version at which the state was captured.

        Returns:
            The reconstructed aggregate.
        """
        raise NotImplementedError(
            "State persistence enabled but _create_from_state() not implemented. "
            "Override in subclass if using state records."
        )

    def _should_save_state(self, event_count: int) -> bool:
        """Determine if a state record should be persisted.

        Default strategy: persist every N events.
        Override in subclasses for different strategies.

        Args:
            event_count: Total number of events for the aggregate.

        Returns:
            True if state should be persisted.
        """
        return event_count > 0 and event_count % self._snapshot_threshold == 0
