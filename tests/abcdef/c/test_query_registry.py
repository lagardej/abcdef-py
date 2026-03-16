"""Tests for query registry and dispatching."""

import pytest

from abcdef.c import QueryRegistry
from tests.abcdef.c.fixtures import (
    DummyQuery,
    DummyQueryHandler,
    DummyResult,
)


def test_query_registry_subscribe() -> None:
    """Test that handlers can be subscribed to query types."""
    registry = QueryRegistry()
    handler = DummyQueryHandler()

    registry.subscribe(DummyQuery, handler.handle)

    assert DummyQuery in registry._handlers


def test_query_registry_publish() -> None:
    """Test that queries are dispatched to registered handlers."""
    registry = QueryRegistry()
    handler = DummyQueryHandler()
    registry.subscribe(DummyQuery, handler.handle)

    query = DummyQuery(key="test_key")
    result = registry.publish(query)

    assert isinstance(result, DummyResult)
    assert result.output == "Queried: test_key"


def test_query_registry_publish_no_handler() -> None:
    """Test that publishing a query with no handler raises ValueError."""
    registry = QueryRegistry()
    query = DummyQuery(key="test_key")

    with pytest.raises(
        ValueError, match="No handler registered for query type DummyQuery"
    ):
        registry.publish(query)


def test_query_registry_duplicate_handler() -> None:
    """Test that registering a handler twice raises ValueError."""
    registry = QueryRegistry()
    handler = DummyQueryHandler()

    registry.subscribe(DummyQuery, handler.handle)

    with pytest.raises(
        ValueError, match="Handler already registered for query type DummyQuery"
    ):
        registry.subscribe(DummyQuery, handler.handle)
