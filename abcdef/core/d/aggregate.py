"""Aggregate Root abstraction."""

from abc import ABC, abstractmethod
from typing import Self

from . import markers


class AggregateId(ABC):
    """Abstract identity for an aggregate.

    Infrastructure-level identity, not a domain concept. Aggregates identify
    themselves to the outside world via their own domain attributes; this ID
    exists solely to satisfy persistence and equality mechanics.

    Subclasses define the concrete storage format and construction logic.
    The serialisation contract is defined by __str__ and from_str, which
    must round-trip: ``cls.from_str(str(id))`` must equal ``id``.
    """

    @abstractmethod
    def __str__(self) -> str:
        """Serialise to a string.

        Returns:
            A stable string representation that can be deserialised
            by from_str.
        """
        ...

    @classmethod
    @abstractmethod
    def from_str(cls, value: str) -> Self:
        """Deserialise from a string produced by __str__.

        Args:
            value: A string previously returned by __str__.

        Returns:
            An AggregateId equal to the original.

        Raises:
            ValueError: If the string is not a valid representation.
        """
        ...

    def __eq__(self, other: object) -> bool:
        """Compare by serialised value.

        Args:
            other: The other object to compare.

        Returns:
            True if both IDs serialise to the same string.
        """
        if not isinstance(other, AggregateId):
            return NotImplemented
        return str(self) == str(other)

    def __hash__(self) -> int:
        """Hash by serialised value.

        Returns:
            Hash of the string representation.
        """
        return hash(str(self))

    def __repr__(self) -> str:
        """Return detailed representation.

        Returns:
            Detailed representation of the aggregate ID.
        """
        return f"{self.__class__.__name__}({str(self)!r})"


@markers.aggregate
class AggregateRoot(ABC):  # noqa: B024
    # B024: AggregateRoot is intentionally abstract without abstract methods.
    # It is a structural base class enforcing identity, equality, and hashing.
    # Subclasses define their own domain-specific behaviour.
    """Base class for Aggregate Roots.

    An Aggregate Root is a cluster of domain objects treated as a single unit.
    It is the only entry point for modifications to the cluster, ensuring that
    all invariants (business rules) within the boundary are enforced.

    Responsibilities:
    - Enforcing invariants within its consistency boundary
    - Providing a stable identity across its lifetime
    - Acting as the unit of persistence (loaded and saved as a whole)

    Identity is carried by an AggregateId — an infrastructure-level UUID wrapper.
    Domain-meaningful identity (e.g. order number, customer code) is expressed
    via the aggregate's own attributes.
    """

    def __init__(self, aggregate_id: AggregateId) -> None:
        """Initialise the aggregate root.

        Args:
            aggregate_id: The unique identity of this aggregate.
        """
        self._id = aggregate_id

    @property
    def id(self) -> AggregateId:
        """Get the aggregate's unique identity.

        Returns:
            The aggregate ID.
        """
        return self._id

    def __eq__(self, other: object) -> bool:
        """Compare aggregates by identity.

        Args:
            other: The other object to compare.

        Returns:
            True if both aggregates have the same ID.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash by identity.

        Returns:
            Hash of the aggregate ID.
        """
        return hash(self._id)
