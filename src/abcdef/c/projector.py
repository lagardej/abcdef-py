"""Projector abstraction for query-side event handling."""

from abc import ABC, abstractmethod

from abcdef.b.event import Event

from . import markers


@markers.projector
class Projector[TEvent: Event](ABC):
    """Base interface for projectors.

    A Projector subscribes to events on an EventBus and updates Documents in a
    DocumentStore. It is the actor that performs the projection -- the Document is the
    result.

    Each Projector is typed to the event type it handles. Fan-out across event types is
    done by registering multiple projectors on an EventBus.
    """

    @abstractmethod
    def project(self, event: TEvent) -> None:
        """Handle an event and update the relevant document(s).

        Args:
            event: The event to project.
        """
        pass
