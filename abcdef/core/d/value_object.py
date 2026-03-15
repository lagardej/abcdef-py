"""Value Object abstraction."""

from dataclasses import dataclass

from . import markers


@markers.value_object
@dataclass(frozen=True)
class ValueObject:
    """Base class for Value Objects.

    A Value Object is:
    - Immutable: attribute assignment and deletion are forbidden
      after construction; any attempt raises ``AttributeError``.
    - Defined by its attributes (compared by value, not identity)
    - Has no concept of identity (two value objects with the same
      attributes are equal)
    - Often used to encapsulate domain concepts with rules

    Immutability is enforced by the frozen dataclass machinery.
    Subclasses must be declared as ``@dataclass(frozen=True)``;
    Python requires all dataclass subclasses of a frozen dataclass
    to also be frozen.

    All attribute values must be hashable. Attributes of unhashable
    types (e.g. list, dict, set) will cause ``__hash__`` to raise
    ``TypeError``.
    """
