"""Event base class for all events dispatched on a bus."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .message import Message

if TYPE_CHECKING:
    import datetime


class Event(Message):
    """Base class for all events dispatched on an EventBus.

    An Event is an immutable record of something that happened. It
    extends Message so it can be published on an EventBus and handled
    by subscribers.

    Subclasses MUST declare a non-empty ``event_type`` class variable.
    This decouples the event's stable identity from the Python class
    name, which may be refactored freely.

    The ``event_type`` must be declared directly on the concrete class
    -- it cannot be satisfied by inheriting it from a parent class.

    Intermediate base classes in the hierarchy may opt out of the check
    by setting ``_abstract_event = True`` directly in their class body.

    Args:
        occurred_at: When the event occurred. Must be supplied by the
            caller; the class never reads the system clock.
    """

    event_type: str = ""
    _abstract_event: bool = False
    occurred_at: datetime.datetime

    def __init_subclass__(cls, **kwargs: object) -> None:
        """Enforce event_type declaration on all concrete subclasses.

        Args:
            **kwargs: Passed through to super().__init_subclass__.

        Raises:
            TypeError: If a concrete subclass does not declare a
                non-empty ``event_type`` directly in its own class
                body.
        """
        super().__init_subclass__(**kwargs)
        if cls.__dict__.get("_abstract_event"):
            return
        if "event_type" not in cls.__dict__ or not cls.__dict__["event_type"]:
            raise TypeError(
                f"{cls.__qualname__} must declare a non-empty "
                f"'event_type' class variable. "
                f"It cannot be inherited from a parent class."
            )

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after construction.

        Subclasses must use ``object.__setattr__(self, name, value)``
        in their ``__init__`` to initialise attributes.

        Args:
            name: Attribute name.
            value: Value to assign.

        Raises:
            AttributeError: Always. Event is immutable.
        """
        raise AttributeError(f"Event is immutable: cannot set attribute {name!r}")

    def __delattr__(self, name: str) -> None:
        """Prevent deletion of attributes.

        Args:
            name: Attribute name.

        Raises:
            AttributeError: Always. Event is immutable.
        """
        raise AttributeError(f"Event is immutable: cannot delete attribute {name!r}")

    def __init__(self, *, occurred_at: datetime.datetime) -> None:
        """Initialise the event.

        Args:
            occurred_at: The timestamp at which this event occurred.
        """
        object.__setattr__(self, "occurred_at", occurred_at)
