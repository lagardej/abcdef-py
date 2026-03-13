"""Shared test helpers for abcdef tests."""

from abcdef.core import AggregateId


def make_id() -> AggregateId:
    """Return a new random AggregateId for use in tests.

    Each call returns a distinct ID backed by a fresh UUID, so tests
    that need multiple IDs can call make_id() multiple times without collision.
    """
    return AggregateId()
