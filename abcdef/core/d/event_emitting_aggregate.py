"""EventEmittingAggregate -- aggregate that raises domain events."""

from . import markers
from .aggregate import AggregateId, AggregateRoot
from .domain_event import DomainEvent


@markers.aggregate
class EventEmittingAggregate(AggregateRoot):
    """Aggregate that raises domain events for publication on the bus.

    Extends AggregateRoot to add event-emitting capability without
    event sourcing. State is not derived from events -- aggregates
    manage their own state directly. Events are raised to notify other
    parts of the system that something happened.

    Use this as the base when:
    - The aggregate needs to communicate state changes via events
    - State does not need to be reconstructed by replaying events

    For event-sourced aggregates (state derived from events), use
    EventSourcedAggregate in de/ instead, which extends this class.

    Subclasses call _emit_event() to record and raise events.
    The repository (or equivalent infrastructure) calls
    _get_uncommitted_events() to retrieve pending events for
    publication, then _mark_events_as_committed() once they have been
    dispatched.
    """

    def __init__(self, aggregate_id: AggregateId) -> None:
        """Initialise with no pending events.

        Args:
            aggregate_id: The unique identity of this aggregate.
        """
        super().__init__(aggregate_id)
        self._pending_events: list[DomainEvent] = []

    def _emit_event(self, event: DomainEvent) -> None:
        """Record an event for later publication.

        The event is appended to the pending list.

        Args:
            event: The domain event to record.
        """
        self._pending_events.append(event)

    def _get_uncommitted_events(self) -> list[DomainEvent]:
        """Return all events recorded but not yet published.

        Called by the repository during save. Not part of the domain
        API.

        Returns:
            List of uncommitted domain events.
        """
        return self._pending_events.copy()

    def _mark_events_as_committed(self) -> None:
        """Clear the pending event list after publication.

        Called by the repository after dispatching events to the bus.
        """
        self._pending_events.clear()
