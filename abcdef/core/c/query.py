"""Core abstractions for queries and handlers."""

from abc import ABC, abstractmethod
from typing import TypeVar

from ..result import Result
from . import markers
from .message import Message

TQuery = TypeVar("TQuery", bound="Query")
TQueryResult = TypeVar("TQueryResult", bound=Result)


@markers.query
class Query(Message):
    """Marker interface for queries.

    A Query represents a request to retrieve data without mutating state.
    Queries are processed by QueryHandlers in the application layer.
    """

    pass


@markers.query_handler
class QueryHandler[TQry: Query, TQryResult: Result](ABC):
    """Base marker interface for query handlers.

    A QueryHandler processes a specific Query type and returns a result
    by reading from document stores.

    """

    @abstractmethod
    def handle(self, query: TQry) -> TQryResult:
        """Execute the query.

        Args:
            query: The query to process.

        Returns:
            The result of executing the query.
        """
        pass
