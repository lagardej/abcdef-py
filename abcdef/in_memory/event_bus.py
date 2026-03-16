"""In-memory implementation of EventBus."""

from collections.abc import Callable
from typing import Any, TypeVar

from abcdef.c import EventBus
from abcdef.core import Event

_TSpecificEvent = TypeVar("_TSpecificEvent", bound=Event)


class InMemoryEventBus[TEvent: Event](EventBus[TEvent]):
    """In-memory EventBus implementation.

    Fans out each published event to all handlers subscribed to that event type.
    Handlers are invoked synchronously in subscription order.

    Generic over TEvent so the bus can be narrowed to a specific event hierarchy (e.g.
    ``InMemoryEventBus[EventSourcedDomainEvent]``) at the composition root while
    remaining usable as ``InMemoryEventBus[Event]`` in general-purpose tests.

    Suitable for testing and lightweight use cases where async dispatch, durability, or
    delivery guarantees are not required.
    """

    def __init__(self) -> None:
        """Initialise the event bus with empty subscriptions."""
        self._handlers: dict[type[Any], list[Callable[[Any], None]]] = {}

    def subscribe(  # type: ignore[override]
        self,
        message_type: type[_TSpecificEvent],
        handler: Callable[[_TSpecificEvent], Any],
    ) -> None:
        """Subscribe a handler to an event type.

        Multiple handlers per event type are supported.

        Args:
            message_type: The event type to subscribe to.
            handler: The handler to invoke when an event of this type is published.
        """
        if message_type not in self._handlers:
            self._handlers[message_type] = []
        self._handlers[message_type].append(handler)

    def publish(self, message: TEvent) -> None:
        """Publish an event to all subscribed handlers.

        Handlers are called synchronously in subscription order.
        Events with no subscribers are silently ignored.

        Args:
            message: The event to publish.
        """
        for handler in self._handlers.get(type(message), []):
            handler(message)
