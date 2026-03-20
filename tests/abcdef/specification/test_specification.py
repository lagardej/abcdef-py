"""Tests for abcdef.specification."""

from abcdef.specification.markers import specification
from abcdef.specification.specification import Specification

from .fixtures import HasValidEmail, IsAdult, Person


def test_concrete_specification_satisfied() -> None:
    """IsAdult returns True for adults."""
    adult = Person(age=25, email="test@example.com")
    spec = IsAdult()
    assert spec.is_satisfied_by(adult) is True


def test_concrete_specification_not_satisfied() -> None:
    """IsAdult returns False for minors."""
    minor = Person(age=15, email="test@example.com")
    spec = IsAdult()
    assert spec.is_satisfied_by(minor) is False


def test_and_combinator_both_satisfied() -> None:
    """& combinator returns True when both specs are satisfied."""
    adult_with_email = Person(age=25, email="test@example.com")
    spec = IsAdult() & HasValidEmail()
    assert spec.is_satisfied_by(adult_with_email) is True


def test_and_combinator_left_false() -> None:
    """& combinator returns False when left spec is not satisfied."""
    minor_with_email = Person(age=15, email="test@example.com")
    spec = IsAdult() & HasValidEmail()
    assert spec.is_satisfied_by(minor_with_email) is False


def test_and_combinator_right_false() -> None:
    """& combinator returns False when right spec is not satisfied."""
    adult_without_email = Person(age=25, email="invalid")
    spec = IsAdult() & HasValidEmail()
    assert spec.is_satisfied_by(adult_without_email) is False


def test_and_combinator_both_false() -> None:
    """& combinator returns False when both specs are not satisfied."""
    minor_without_email = Person(age=15, email="invalid")
    spec = IsAdult() & HasValidEmail()
    assert spec.is_satisfied_by(minor_without_email) is False


def test_or_combinator_both_satisfied() -> None:
    """| combinator returns True when both specs are satisfied."""
    adult_with_email = Person(age=25, email="test@example.com")
    spec = IsAdult() | HasValidEmail()
    assert spec.is_satisfied_by(adult_with_email) is True


def test_or_combinator_left_true() -> None:
    """| combinator returns True when left spec is satisfied."""
    adult_without_email = Person(age=25, email="invalid")
    spec = IsAdult() | HasValidEmail()
    assert spec.is_satisfied_by(adult_without_email) is True


def test_or_combinator_right_true() -> None:
    """| combinator returns True when right spec is satisfied."""
    minor_with_email = Person(age=15, email="test@example.com")
    spec = IsAdult() | HasValidEmail()
    assert spec.is_satisfied_by(minor_with_email) is True


def test_or_combinator_both_false() -> None:
    """| combinator returns False when both specs are not satisfied."""
    minor_without_email = Person(age=15, email="invalid")
    spec = IsAdult() | HasValidEmail()
    assert spec.is_satisfied_by(minor_without_email) is False


def test_invert_combinator_true_to_false() -> None:
    """~ combinator negates True to False."""
    adult = Person(age=25, email="test@example.com")
    spec = ~IsAdult()
    assert spec.is_satisfied_by(adult) is False


def test_invert_combinator_false_to_true() -> None:
    """~ combinator negates False to True."""
    minor = Person(age=15, email="test@example.com")
    spec = ~IsAdult()
    assert spec.is_satisfied_by(minor) is True


def test_nested_composition_and_then_or() -> None:
    """(A & B) | C combines specs correctly."""
    # (adult & has_valid_email) or (adult) = True for any adult
    child_with_email = Person(age=15, email="test@example.com")
    adult_no_email = Person(age=25, email="invalid")

    spec = (IsAdult() & HasValidEmail()) | IsAdult()

    assert spec.is_satisfied_by(adult_no_email) is True
    assert spec.is_satisfied_by(child_with_email) is False


def test_specification_decorator_adds_marker() -> None:
    """@specification decorator adds __specification_type__ attribute."""

    @specification
    class EmptySpec(Specification):
        """Empty specification for testing."""

        def is_satisfied_by(self, candidate: object) -> bool:
            """Return True for any candidate.

            Args:
                candidate: The object to evaluate.

            Returns:
                Always True.
            """
            return True

    assert EmptySpec.__specification_type__ == "specification"  # type: ignore[attr-defined]


def test_specification_marker_inherited() -> None:
    """@specification marker is inherited by subclasses."""

    @specification
    class ParentSpec(Specification):
        """Parent specification for inheritance test."""

        def is_satisfied_by(self, candidate: object) -> bool:
            """Return True for any candidate.

            Args:
                candidate: The object to evaluate.

            Returns:
                Always True.
            """
            return True

    class ChildSpec(ParentSpec):
        """Child specification inherits marker."""

        def is_satisfied_by(self, candidate: object) -> bool:
            """Return False for any candidate.

            Args:
                candidate: The object to evaluate.

            Returns:
                Always False.
            """
            return False

    assert ChildSpec.__specification_type__ == "specification"  # type: ignore[attr-defined]
