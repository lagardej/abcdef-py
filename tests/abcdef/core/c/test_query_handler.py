"""Tests for query handlers."""

import pytest

from abcdef.core import QueryHandler
from tests.abcdef.core.c.fixtures import (
    DummyQuery,
    DummyQueryHandler,
    DummyResult,
)


def test_query_handler_can_be_instantiated() -> None:
    """Test that a QueryHandler subclass can be instantiated."""
    handler = DummyQueryHandler()
    assert handler is not None


def test_query_handler_handle_method() -> None:
    """Test that QueryHandler.handle() can be called."""
    handler = DummyQueryHandler()
    query = DummyQuery(key="test_key")

    result = handler.handle(query)

    assert isinstance(result, DummyResult)
    assert result.output == "Queried: test_key"


def test_query_handler_is_abstract() -> None:
    """Test that QueryHandler cannot be instantiated directly."""
    with pytest.raises(TypeError):
        QueryHandler()  # type: ignore[arg-type]
