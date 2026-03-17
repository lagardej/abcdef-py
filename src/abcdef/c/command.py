"""Core abstractions for commands and handlers."""

from abc import ABC, abstractmethod

from abcdef.b.message import Message
from abcdef.b.result import Result

from . import markers


@markers.command
class Command(Message):
    """Marker interface for commands.

    A Command represents an intent to perform an action that mutates state.
    Commands are processed by CommandHandlers in the application layer.
    """

    pass


@markers.command_handler
class CommandHandler[TCmd: Command, TRes: Result](ABC):
    """Base marker interface for command handlers.

    A CommandHandler processes a specific Command type and orchestrates changes to
    aggregates or other domain objects.
    """

    @abstractmethod
    def handle(self, command: TCmd) -> TRes:
        """Execute the command.

        Args:
            command: The command to process.

        Returns:
            The result of executing the command.
        """
        pass
