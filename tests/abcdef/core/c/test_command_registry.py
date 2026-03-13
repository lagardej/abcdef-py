"""Tests for command registry and dispatching."""

import pytest

from abcdef.core import CommandRegistry
from tests.abcdef.core.c.fixtures import (
    DummyCommand,
    DummyCommandHandler,
    DummyResult,
)


def test_command_registry_subscribe() -> None:
    """Test that handlers can be subscribed to command types."""
    registry = CommandRegistry()
    handler = DummyCommandHandler()

    registry.subscribe(DummyCommand, handler.handle)

    assert DummyCommand in registry._handlers


def test_command_registry_publish() -> None:
    """Test that commands are dispatched to registered handlers."""
    registry = CommandRegistry()
    handler = DummyCommandHandler()
    registry.subscribe(DummyCommand, handler.handle)

    command = DummyCommand(value="test")
    result = registry.publish(command)

    assert isinstance(result, DummyResult)
    assert result.output == "Handled: test"


def test_command_registry_publish_no_handler() -> None:
    """Test that publishing a command with no handler raises ValueError."""
    registry = CommandRegistry()
    command = DummyCommand(value="test")

    with pytest.raises(
        ValueError, match="No handler registered for command type DummyCommand"
    ):
        registry.publish(command)


def test_command_registry_duplicate_handler() -> None:
    """Test that registering a handler twice raises ValueError."""
    registry = CommandRegistry()
    handler = DummyCommandHandler()

    registry.subscribe(DummyCommand, handler.handle)

    with pytest.raises(
        ValueError, match="Handler already registered for command type DummyCommand"
    ):
        registry.subscribe(DummyCommand, handler.handle)
