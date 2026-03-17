"""Core abstractions for message buses."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from abcdef.b.event import Event

_TSpecificEvent = TypeVar("_TSpecificEvent", bound=Event)


class MessageBus[TMessage](ABC):
    """Base interface for message buses.

    A MessageBus handles publication and subscription of messages.
    Implementations manage handler registration and dispatch.
    """

    @abstractmethod
    def subscribe(
        self, message_type: type[TMessage], handler: Callable[[TMessage], Any]
    ) -> None:
        """Subscribe a handler to a message type.

        Args:
            message_type: The type of message to subscribe to.
            handler: The handler function to invoke when a message is published.
        """
        pass

    @abstractmethod
    def publish(self, message: TMessage) -> Any:  # noqa: ANN401
        # ANN401: publish() is intentionally typed as Any because CommandBus, EventBus,
        # and QueryBus each return different types (TResult, None, TQueryResult). A
        # single abstract signature cannot express all three without Any or a more
        # complex overload structure. Concrete subclasses (CommandRegistry,
        # QueryRegistry, InMemoryEventBus) narrow the return type appropriately.
        """Publish a message to all subscribed handlers.

        Args:
            message: The message to publish.

        Returns:
            The result from the handler (if single handler) or aggregated results.
        """
        pass


class CommandBus[TCommand](MessageBus[TCommand]):
    """Specialised message bus for commands.

    A CommandBus routes commands to their single handler.
    Each command type has exactly one handler.
    """

    pass


class EventBus[TEvent: Event](MessageBus[TEvent]):
    """Specialised message bus for domain events.

    An EventBus publishes domain events to multiple subscribers.
    Events are immutable facts about what happened in the domain.
    """

    @abstractmethod
    def subscribe(  # type: ignore[override]
        self,
        message_type: type[_TSpecificEvent],
        handler: Callable[[_TSpecificEvent], Any],
    ) -> None:
        """Subscribe a handler to a specific event subtype.

        Overrides MessageBus.subscribe to allow handlers typed for a concrete event
        subtype (e.g. ``Callable[[OrderPlaced], Any]``) rather than the bus's base
        event type. The method-level TypeVar ``_TSpecificEvent`` binds ``message_type``
        and ``handler`` together so Pyright accepts narrowly-typed handlers at call
        sites.

        Args:
            message_type: The concrete event type to subscribe to.
            handler: The handler to invoke when an event of this type is published.
        """
        pass


class QueryBus[TQuery](MessageBus[TQuery]):
    """Specialised message bus for queries.

    A QueryBus routes queries to their single handler.
    Each query type has exactly one handler.
    """

    pass
