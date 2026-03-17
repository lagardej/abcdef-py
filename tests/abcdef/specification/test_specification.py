"""Tests for abcdef.specification."""

import pytest

from abcdef.specification import Specification
from abcdef.specification.markers import specification as specification_marker

# ---------------------------------------------------------------------------
# Concrete specification fixtures
# ---------------------------------------------------------------------------


class IsEven(Specification[int]):
    """Satisfied when the candidate integer is even."""

    def is_satisfied_by(self, candidate: int) -> bool:
        """Return True if candidate is even."""
        return candidate % 2 == 0


class IsPositive(Specification[int]):
    """Satisfied when the candidate integer is positive."""

    def is_satisfied_by(self, candidate: int) -> bool:
        """Return True if candidate is greater than zero."""
        return candidate > 0


class IsShort(Specification[str]):
    """Satisfied when the candidate string has fewer than 5 characters."""

    def is_satisfied_by(self, candidate: str) -> bool:
        """Return True if candidate is shorter than 5 characters."""
        return len(candidate) < 5


# ---------------------------------------------------------------------------
# Specification.is_satisfied_by
# ---------------------------------------------------------------------------


class TestIsSatisfiedBy:
    """Tests for the is_satisfied_by contract."""

    def test_satisfied_returns_true(self) -> None:
        """is_satisfied_by returns True when the rule is met."""
        assert IsEven().is_satisfied_by(4) is True

    def test_not_satisfied_returns_false(self) -> None:
        """is_satisfied_by returns False when the rule is not met."""
        assert IsEven().is_satisfied_by(3) is False

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Specification cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Specification()  # type: ignore[abstract]


# ---------------------------------------------------------------------------
# AndSpecification (__and__)
# ---------------------------------------------------------------------------


class TestAndSpecification:
    """Tests for the & combinator."""

    def test_and_satisfied_when_both_satisfied(self) -> None:
        """& is satisfied when both operands are satisfied."""
        spec = IsEven() & IsPositive()
        assert spec.is_satisfied_by(4) is True

    def test_and_not_satisfied_when_left_fails(self) -> None:
        """& is not satisfied when the left operand fails."""
        spec = IsEven() & IsPositive()
        assert spec.is_satisfied_by(3) is False

    def test_and_not_satisfied_when_right_fails(self) -> None:
        """& is not satisfied when the right operand fails."""
        spec = IsEven() & IsPositive()
        assert spec.is_satisfied_by(-2) is False

    def test_and_not_satisfied_when_both_fail(self) -> None:
        """& is not satisfied when both operands fail."""
        spec = IsEven() & IsPositive()
        assert spec.is_satisfied_by(-3) is False

    def test_and_returns_specification(self) -> None:
        """& returns a Specification instance."""
        spec = IsEven() & IsPositive()
        assert isinstance(spec, Specification)

    def test_and_is_chainable(self) -> None:
        """& can be chained across three specifications."""

        class IsLessThanTen(Specification[int]):
            def is_satisfied_by(self, candidate: int) -> bool:
                return candidate < 10

        spec = IsEven() & IsPositive() & IsLessThanTen()
        assert spec.is_satisfied_by(4) is True
        assert spec.is_satisfied_by(12) is False
        assert spec.is_satisfied_by(-2) is False


# ---------------------------------------------------------------------------
# OrSpecification (__or__)
# ---------------------------------------------------------------------------


class TestOrSpecification:
    """Tests for the | combinator."""

    def test_or_satisfied_when_both_satisfied(self) -> None:
        """| is satisfied when both operands are satisfied."""
        spec = IsEven() | IsPositive()
        assert spec.is_satisfied_by(4) is True

    def test_or_satisfied_when_only_left_satisfied(self) -> None:
        """| is satisfied when only the left operand is satisfied."""
        spec = IsEven() | IsPositive()
        assert spec.is_satisfied_by(-2) is True

    def test_or_satisfied_when_only_right_satisfied(self) -> None:
        """| is satisfied when only the right operand is satisfied."""
        spec = IsEven() | IsPositive()
        assert spec.is_satisfied_by(3) is True

    def test_or_not_satisfied_when_both_fail(self) -> None:
        """| is not satisfied when both operands fail."""
        spec = IsEven() | IsPositive()
        assert spec.is_satisfied_by(-3) is False

    def test_or_returns_specification(self) -> None:
        """| returns a Specification instance."""
        spec = IsEven() | IsPositive()
        assert isinstance(spec, Specification)

    def test_or_is_chainable(self) -> None:
        """| can be chained across three specifications."""

        class IsZero(Specification[int]):
            def is_satisfied_by(self, candidate: int) -> bool:
                return candidate == 0

        spec = IsEven() | IsPositive() | IsZero()
        assert spec.is_satisfied_by(0) is True
        assert spec.is_satisfied_by(1) is True
        assert spec.is_satisfied_by(-3) is False


# ---------------------------------------------------------------------------
# NotSpecification (__invert__)
# ---------------------------------------------------------------------------


class TestNotSpecification:
    """Tests for the ~ combinator."""

    def test_not_satisfied_when_inner_not_satisfied(self) -> None:
        """~ is satisfied when the inner specification is not satisfied."""
        spec = ~IsEven()
        assert spec.is_satisfied_by(3) is True

    def test_not_not_satisfied_when_inner_satisfied(self) -> None:
        """~ is not satisfied when the inner specification is satisfied."""
        spec = ~IsEven()
        assert spec.is_satisfied_by(4) is False

    def test_not_returns_specification(self) -> None:
        """~ returns a Specification instance."""
        spec = ~IsEven()
        assert isinstance(spec, Specification)

    def test_double_not_round_trips(self) -> None:
        """Applying ~ twice restores the original behaviour."""
        spec = ~~IsEven()
        assert spec.is_satisfied_by(4) is True
        assert spec.is_satisfied_by(3) is False


# ---------------------------------------------------------------------------
# Mixed combinators
# ---------------------------------------------------------------------------


class TestMixedCombinators:
    """Tests for combinations of &, |, and ~."""

    def test_not_and(self) -> None:
        """~(A & B) is satisfied when at least one operand is not satisfied."""
        spec = ~(IsEven() & IsPositive())
        assert spec.is_satisfied_by(3) is True  # odd positive
        assert spec.is_satisfied_by(-2) is True  # even negative
        assert spec.is_satisfied_by(4) is False  # even positive

    def test_and_with_not(self) -> None:
        """A & ~B is satisfied when A is satisfied and B is not."""
        spec = IsEven() & ~IsPositive()
        assert spec.is_satisfied_by(-2) is True
        assert spec.is_satisfied_by(4) is False
        assert spec.is_satisfied_by(-3) is False

    def test_or_with_not(self) -> None:
        """~A | B is satisfied when A fails or B is satisfied."""
        spec = ~IsEven() | IsPositive()
        assert spec.is_satisfied_by(3) is True  # odd positive
        assert spec.is_satisfied_by(4) is True  # even positive
        assert spec.is_satisfied_by(-3) is True  # odd negative
        assert spec.is_satisfied_by(-2) is False  # even negative


# ---------------------------------------------------------------------------
# @specification marker
# ---------------------------------------------------------------------------


class TestSpecificationMarker:
    """Tests for the @specification decorator."""

    def test_marker_sets_specification_type(self) -> None:
        """@specification sets __specification_type__ to 'specification'."""

        @specification_marker
        class MySpec(Specification[int]):
            def is_satisfied_by(self, candidate: int) -> bool:
                return True

        assert MySpec.__specification_type__ == "specification"  # type: ignore[attr-defined]

    def test_marker_returns_class_unchanged(self) -> None:
        """@specification returns the decorated class itself."""

        class MySpec(Specification[int]):
            def is_satisfied_by(self, candidate: int) -> bool:
                return True

        result = specification_marker(MySpec)
        assert result is MySpec

    def test_marker_inherited_by_subclass(self) -> None:
        """@specification marker is inherited by subclasses."""

        @specification_marker
        class Base(Specification[int]):
            def is_satisfied_by(self, candidate: int) -> bool:
                return True

        class Sub(Base):
            pass

        assert Sub.__specification_type__ == "specification"  # type: ignore[attr-defined]
