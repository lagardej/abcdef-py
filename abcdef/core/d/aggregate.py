"""Aggregate Root abstraction."""

from abc import ABC
from uuid import UUID, uuid4

from . import markers


class AggregateId:
    """Internal identity for an aggregate.

    Infrastructure-level identity, not a domain concept. Aggregates identify
    themselves to the outside world via their own domain attributes; this ID
    exists solely to satisfy persistence and equality mechanics.

    Accepts a UUID, a UUID string, or nothing on construction; strings are
    coerced to UUID so the stored value is always canonical. If omitted, a
    new random UUID is generated.

    Attributes:
        value: The canonical UUID representing this identity.
    """

    def __init__(self, value: UUID | str | None = None) -> None:
        """Initialise the aggregate ID.

        Args:
            value: A UUID, a UUID string, or None to generate a new UUID.
        """
        if value is None:
            self.__dict__["_value"] = uuid4()
        elif isinstance(value, UUID):
            self.__dict__["_value"] = value
        else:
            self.__dict__["_value"] = UUID(value)

    @property
    def value(self) -> UUID:
        """The canonical UUID for this identity.

        Returns:
            The UUID value.
        """
        return self.__dict__["_value"]

    def __setattr__(self, name: str, val: object) -> None:
        """Prevent mutation after construction.

        Raises:
            AttributeError: Always — AggregateId is immutable.
        """
        raise AttributeError("AggregateId is immutable")

    def __eq__(self, other: object) -> bool:
        """Compare by UUID value.

        Args:
            other: The other object to compare.

        Returns:
            True if both IDs hold the same UUID.
        """
        if not isinstance(other, AggregateId):
            return NotImplemented
        return self.__dict__["_value"] == other.__dict__["_value"]

    def __hash__(self) -> int:
        """Hash by UUID value.

        Returns:
            Hash of the underlying UUID.
        """
        return hash(self.__dict__["_value"])

    def __str__(self) -> str:
        """Return the UUID as a string.

        Returns:
            Canonical UUID string representation.
        """
        return str(self.__dict__["_value"])

    def __repr__(self) -> str:
        """Return detailed representation.

        Returns:
            Detailed representation of the aggregate ID.
        """
        return f"AggregateId({self.__dict__['_value']!r})"


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
