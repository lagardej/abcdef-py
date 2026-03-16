"""Tests for command handlers."""

import pytest

from abcdef.c import CommandHandler
from tests.abcdef.c.fixtures import (
    DummyCommand,
    DummyCommandHandler,
    DummyResult,
)


def test_command_handler_can_be_instantiated() -> None:
    """Test that a CommandHandler subclass can be instantiated."""
    handler = DummyCommandHandler()
    assert handler is not None


def test_command_handler_handle_method() -> None:
    """Test that CommandHandler.handle() can be called."""
    handler = DummyCommandHandler()
    command = DummyCommand(value="test")

    result = handler.handle(command)

    assert isinstance(result, DummyResult)
    assert result.output == "Handled: test"


def test_command_handler_is_abstract() -> None:
    """Test that CommandHandler cannot be instantiated directly."""
    with pytest.raises(TypeError):
        CommandHandler()  # type: ignore[arg-type]
