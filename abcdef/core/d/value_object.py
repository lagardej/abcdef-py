"""Value Object abstraction."""

from . import markers


@markers.value_object
class ValueObject:
    """Base class for Value Objects.

    A Value Object is:
    - Immutable (once created, it cannot be changed)
    - Defined by its attributes (compared by value, not identity)
    - Has no concept of identity (two value objects with same attributes are equal)
    - Often used to encapsulate domain concepts with rules

    Subclasses should be implemented as immutable (use frozen dataclasses or similar).
    """

    def __eq__(self, other: object) -> bool:
        """Compare by value.

        Args:
            other: The other object to compare.

        Returns:
            True if both objects have the same attributes.
        """
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.__dict__ == other.__dict__

    def __hash__(self) -> int:
        """Hash by value.

        Returns:
            Hash of the object attributes.
        """
        return hash(tuple(sorted(self.__dict__.items())))
