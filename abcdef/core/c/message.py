"""Message base class for all bus-dispatched messages."""


class Message:
    """Base class for all messages dispatched on a bus.

    A Message is the common root for Commands, Queries, and Events.
    It carries no data of its own; its purpose is to provide a single
    type that buses and handlers can constrain against.
    """

    pass
