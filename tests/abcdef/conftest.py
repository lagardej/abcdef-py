"""Shared test helpers for abcdef tests."""

from typing import Self
from uuid import uuid4

from abcdef.core import AggregateId


class StrAggregateId(AggregateId):
    """Minimal string-backed AggregateId for use in tests.

    Exists solely to let tests exercise the AggregateId contract without
    depending on any production implementation.
    """

    _value: str

    def __init__(self, value: str) -> None:
        """Initialise with a plain string."""
        object.__setattr__(self, "_value", value)

    def __str__(self) -> str:
        """Return the backing string."""
        return self._value

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Reconstruct from a string."""
        return cls(value)


def make_id() -> StrAggregateId:
    """Return a new distinct StrAggregateId for use in tests.

    Each call returns a unique ID so tests that need multiple IDs
    can call make_id() multiple times without collision.
    """
    return StrAggregateId(str(uuid4()))
