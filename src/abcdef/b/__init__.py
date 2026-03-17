"""Shared foundational primitives for the rest of abcdef."""

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
