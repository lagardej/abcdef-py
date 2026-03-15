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

    All attribute values must be hashable. Attributes of unhashable types (e.g. list,
    dict, set) will cause ``__hash__`` to raise ``TypeError`` naming the offending
    attribute.
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

        All attribute values must be hashable. Raises ``TypeError`` naming the
        offending attribute if an unhashable value is encountered.

        Returns:
            Hash of the object attributes.

        Raises:
            TypeError: If any attribute value is not hashable.
        """
        items: list[tuple[str, object]] = sorted(self.__dict__.items())
        for key, value in items:
            try:
                hash(value)
            except TypeError:
                raise TypeError(
                    f"{self.__class__.__name__}.{key} is not hashable. "
                    f"ValueObject attributes must be hashable types."
                ) from None
        return hash(tuple(items))
