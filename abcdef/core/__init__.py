"""Core package -- abstract base classes and marker interfaces."""

from .event import Event
from .markers import _get_marker
from .message import Message
from .result import Result

__all__ = [
    "Event",
    "Message",
    "Result",
    "_get_marker",
]
