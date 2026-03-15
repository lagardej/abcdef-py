"""Specification pattern for abcdef.

Provides the Specification ABC and combinators for composing
business rules without polluting domain or application logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Specification[T](ABC):
    """Abstract base for domain specifications.

    A Specification encapsulates a single business rule as a
    reusable, composable predicate.  Subclasses implement
    ``is_satisfied_by`` to express the rule.

    Combinators:

    - ``spec_a & spec_b`` — both must be satisfied
    - ``spec_a | spec_b`` — at least one must be satisfied
    - ``~spec``           — the inner specification must not
      be satisfied

    Example::

        class IsAdult(Specification[Person]):
            def is_satisfied_by(self, candidate: Person) -> bool:
                return candidate.age >= 18

        class HasValidEmail(Specification[Person]):
            def is_satisfied_by(self, candidate: Person) -> bool:
                return "@" in candidate.email

        eligible = IsAdult() & HasValidEmail()
        eligible.is_satisfied_by(person)
    """

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Return True if the candidate satisfies this specification.

        Args:
            candidate: The object to evaluate.

        Returns:
            True if the specification is satisfied, False otherwise.
        """

    def __and__(self, other: Specification[T]) -> Specification[T]:
        """Return a specification satisfied when both are satisfied.

        Args:
            other: The specification to combine with.

        Returns:
            An AndSpecification combining self and other.
        """
        return _AndSpecification(self, other)

    def __or__(self, other: Specification[T]) -> Specification[T]:
        """Return a specification satisfied when either is satisfied.

        Args:
            other: The specification to combine with.

        Returns:
            An OrSpecification combining self and other.
        """
        return _OrSpecification(self, other)

    def __invert__(self) -> Specification[T]:
        """Return a specification satisfied when this one is not.

        Returns:
            A NotSpecification wrapping self.
        """
        return _NotSpecification(self)


class _AndSpecification[T](Specification[T]):
    """Satisfied when both left and right are satisfied."""

    def __init__(
        self,
        left: Specification[T],
        right: Specification[T],
    ) -> None:
        """Initialise with left and right operands.

        Args:
            left: The first specification.
            right: The second specification.
        """
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Return True if both specifications are satisfied.

        Args:
            candidate: The object to evaluate.

        Returns:
            True if both left and right are satisfied.
        """
        return self._left.is_satisfied_by(candidate) and self._right.is_satisfied_by(
            candidate
        )


class _OrSpecification[T](Specification[T]):
    """Satisfied when at least one of left or right is satisfied."""

    def __init__(
        self,
        left: Specification[T],
        right: Specification[T],
    ) -> None:
        """Initialise with left and right operands.

        Args:
            left: The first specification.
            right: The second specification.
        """
        self._left = left
        self._right = right

    def is_satisfied_by(self, candidate: T) -> bool:
        """Return True if either specification is satisfied.

        Args:
            candidate: The object to evaluate.

        Returns:
            True if left or right (or both) are satisfied.
        """
        return self._left.is_satisfied_by(candidate) or self._right.is_satisfied_by(
            candidate
        )


class _NotSpecification[T](Specification[T]):
    """Satisfied when the inner specification is not satisfied."""

    def __init__(self, inner: Specification[T]) -> None:
        """Initialise with the inner specification to negate.

        Args:
            inner: The specification to negate.
        """
        self._inner = inner

    def is_satisfied_by(self, candidate: T) -> bool:
        """Return True if the inner specification is not satisfied.

        Args:
            candidate: The object to evaluate.

        Returns:
            True if the inner specification is not satisfied.
        """
        return not self._inner.is_satisfied_by(candidate)


def specification[T](cls: T) -> T:
    """Mark a class as a Specification.

    A Specification encapsulates complex business rules that can be
    reused across multiple contexts.  Marker is inherited by
    subclasses.

    Args:
        cls: The class to mark as a specification.

    Returns:
        The class with ``__ddd_type__ = "specification"`` metadata.
    """
    cls.__ddd_type__ = "specification"  # type: ignore[attr-defined]
    return cls
