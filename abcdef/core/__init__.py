"""Core package -- abstract base classes and marker interfaces."""

from .event import Event
from .message import Message
from .registry import ClassRegistry
from .result import Result

__all__ = [
    "ClassRegistry",
    "Event",
    "Message",
    "Result",
]
