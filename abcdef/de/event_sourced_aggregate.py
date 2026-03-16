"""Event-sourced aggregate with version tracking and event application."""

from abc import abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from ..core.registry import ClassRegistry
from ..d import AggregateId
from ..d.event_emitting_aggregate import EventEmittingAggregate
from .event_sourced_domain_event import EventSourcedDomainEvent


class AggregateRegistry(ClassRegistry["type[EventSourcedAggregate]"]):
    """Registry of EventSourcedAggregate subclasses keyed by aggregate_type.

    A plain, injectable class with no global state. Callers create an instance and
    register aggregate classes into it explicitly. Pass the registry to
    EventSourcedRepository at construction time.
    """


@dataclass(frozen=True)
class AggregateState:
    """Immutable base for aggregate state snapshots.

    Aggregate state is a point-in-time record of an aggregate's data, used for
    performance optimisation in event sourcing (snapshots).

    All subclasses must be frozen dataclasses. Declare them with
    ``@dataclass(frozen=True)`` or rely on inheritance from this base, which is itself
    a frozen dataclass. Subclasses that are plain classes (not dataclasses) will not
    have immutability enforced at runtime.

    Frozen dataclasses provide:
    - Immutability: assignment raises ``AttributeError`` after construction.
    - Value equality: ``__eq__`` compares fields by value.
    - Hashability: ``__hash__`` is derived from field values.
    - Readability: ``__repr__`` includes the class name and all fields.
    """

    pass


class EventSourcedAggregate[TState: AggregateState](
    EventEmittingAggregate[EventSourcedDomainEvent]
):
    """Aggregate optimised for event sourcing with version tracking.

    Extends EventEmittingAggregate to add event sourcing concerns:
    - Applying events to state immediately on emit (event application pattern)
    - Version tracking for optimistic locking and snapshot delta calculations
    - Replaying historical events to reconstruct state
    - Generic state type for type-safe snapshots

    The version increments with each event, enabling:
    - Concurrency control (detect conflicting updates)
    - Snapshot delta calculations
    - Event replay validation

    ``aggregate_type`` enforcement is inherited from AggregateRoot. All concrete
    subclasses must declare a non-empty ``aggregate_type`` directly in their class body.

    Intermediate base classes may opt out by setting ``_abstract_aggregate = True``
    directly in their class body.

    Subclasses must also implement:
    - _apply_event() -- apply emitted events to the aggregate's state
    - create_state() -- create a state snapshot at the current moment
    - load_from_state() -- restore state from a persisted state record
    """

    _abstract_aggregate = True

    def __init__(self, aggregate_id: AggregateId) -> None:
        """Initialise a new event-sourced aggregate with no history.

        Args:
            aggregate_id: The unique identity of this aggregate.
        """
        super().__init__(aggregate_id)
        self._version = 0
        self._base_version = 0

    @classmethod
    def from_state(
        cls,
        aggregate_id: AggregateId,
        state: TState,
        version: int,
    ) -> "EventSourcedAggregate[TState]":
        """Reconstruct an aggregate from a persisted state record.

        Creates the aggregate, restores state via load_from_state, and sets both
        version and base_version to the given version so that the state threshold is
        calculated as a delta from this point.

        Args:
            aggregate_id: The identity of the aggregate.
            state: The state record to restore from.
            version: The event version at which the state was captured.

        Returns:
            The reconstructed aggregate instance.
        """
        instance = cls.__new__(cls)
        EventSourcedAggregate.__init__(instance, aggregate_id)
        instance.load_from_state(state)
        instance._version = version
        instance._base_version = version
        return instance

    @property
    def version(self) -> int:
        """Current version of this aggregate.

        Increments with each event. Used for optimistic locking, snapshot delta
        calculations, and event replay tracking.

        Returns:
            The current version number.
        """
        return self._version

    @property
    def base_version(self) -> int:
        """Version at which this aggregate was last loaded or state persisted.

        Used by the repository to calculate the delta since the last state save:
        ``version - base_version >= threshold`` triggers a new state save. Updated by
        _mark_state_saved() after a state record is persisted.

        Returns:
            The base version number.
        """
        return self._base_version

    def _get_uncommitted_events(self) -> list[EventSourcedDomainEvent]:
        """Return all events recorded but not yet persisted.

        Returns:
            List of uncommitted event-sourced domain events.
        """
        return self._pending_events.copy()

    def _emit_event(self, event: EventSourcedDomainEvent) -> None:
        """Record an event, apply it to state, and increment version.

        Overrides EventEmittingAggregate._emit_event to add:
        1. Immediate application of the event to state
        2. Version increment

        Args:
            event: The event-sourced domain event to record and apply.
        """
        super()._emit_event(event)
        self._apply_event(event)
        self._version += 1

    def _mark_state_saved(self) -> None:
        """Update the base version to the current version after a state save.

        Called by the repository after successfully persisting a state record. Resets
        the delta counter so the next state threshold is calculated from this point
        forward.
        """
        self._base_version = self._version

    def _load_from_history(self, events: Sequence[EventSourcedDomainEvent]) -> None:
        """Reconstruct aggregate state by replaying historical events.

        Called by the repository when rebuilding an aggregate from stored events. Does
        NOT record events as uncommitted -- historical events are already committed.
        Subclasses never need to call or override this.

        Args:
            events: Historical domain events in chronological order.
        """
        for event in events:
            self._apply_event(event)
            self._version += 1

    @abstractmethod
    def _apply_event(self, event: EventSourcedDomainEvent) -> None:
        """Apply a single event to the aggregate's internal state.

        Subclasses MUST implement this to define how each event type changes state.
        Called by _emit_event (new events) and _load_from_history (historical events).
        Never called directly by application or repository code.

        Args:
            event: The domain event to apply.
        """
        pass

    @abstractmethod
    def create_state(self) -> TState:
        """Capture the aggregate's current state for persistence.

        Paired with load_from_state: create_state serialises, load_from_state
        deserialises. The repository calls this when persisting a state record.

        Returns:
            The aggregate's current state.
        """
        pass

    @abstractmethod
    def load_from_state(self, state: TState) -> None:
        """Restore the aggregate's state from a persisted state record.

        Paired with create_state: called by from_state() during reconstruction from a
        persisted state record. Must restore all domain state that create_state
        serialised.

        Args:
            state: The state record to restore from.
        """
        pass
