"""Tests for Value Object."""

from dataclasses import dataclass

import pytest

from abcdef.core import ValueObject


@dataclass(frozen=True)
class Money(ValueObject):
    """Test value object."""

    amount: float
    currency: str


@dataclass(frozen=True)
class TaggedItem(ValueObject):
    """Value object with an unhashable attribute (list)."""

    name: str
    tags: list[str]


class TestValueObject:
    """Tests for ValueObject base class."""

    def test_value_object_equality_by_value(self) -> None:
        """Test that value objects are compared by value."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(100.0, "USD")
        assert vo1 == vo2

    def test_value_object_inequality_by_value(self) -> None:
        """Test that value objects with different values are not equal."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(200.0, "USD")
        assert vo1 != vo2

    def test_value_object_inequality_different_type(self) -> None:
        """Test that value objects are not equal to other types."""
        vo = Money(100.0, "USD")
        assert vo != "100.0 USD"
        assert vo != 100.0

    def test_eq_returns_not_implemented_for_foreign_type(self) -> None:
        """__eq__ returns NotImplemented (not None) for incompatible types."""
        vo = Money(100.0, "USD")
        result = vo.__eq__("not a money")
        assert result is NotImplemented

    def test_value_object_hashable(self) -> None:
        """Test that value objects can be used in sets."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(100.0, "USD")
        vo3 = Money(200.0, "USD")

        vo_set = {vo1, vo2, vo3}
        assert len(vo_set) == 2

    def test_value_object_hashable_in_dict(self) -> None:
        """Test that value objects can be used as dict keys."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(100.0, "USD")

        vo_dict = {vo1: "price"}
        assert vo_dict[vo2] == "price"

    def test_value_object_identity_not_compared(self) -> None:
        """Test that identity is not used for comparison."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(100.0, "USD")

        assert vo1 is not vo2
        assert vo1 == vo2

    def test_value_object_hash_derived_from_attributes(self) -> None:
        """Hash is derived from attribute values, not object identity."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(100.0, "USD")
        assert vo1 is not vo2
        assert hash(vo1) == hash(vo2)

    def test_value_object_different_attributes_different_hashes(self) -> None:
        """Value objects with different attributes produce different hashes."""
        vo1 = Money(100.0, "USD")
        vo2 = Money(200.0, "USD")
        assert hash(vo1) != hash(vo2)

    def test_hash_raises_type_error_for_unhashable_attribute(self) -> None:
        """__hash__ raises TypeError for unhashable attributes."""
        vo = TaggedItem("widget", ["a", "b"])
        with pytest.raises(TypeError):
            hash(vo)


class TestValueObjectImmutability:
    """Tests for ValueObject immutability enforcement."""

    def test_setting_attribute_after_construction_raises(self) -> None:
        """Setting an attribute after construction raises FrozenInstanceError."""
        vo = Money(100.0, "USD")
        with pytest.raises(AttributeError):
            vo.amount = 200.0  # type: ignore[misc]

    def test_deleting_attribute_raises(self) -> None:
        """Deleting an attribute raises FrozenInstanceError."""
        vo = Money(100.0, "USD")
        with pytest.raises(AttributeError):
            del vo.amount  # type: ignore[misc]

    def test_adding_new_attribute_after_construction_raises(self) -> None:
        """Adding a new attribute after construction raises FrozenInstanceError."""
        vo = Money(100.0, "USD")
        with pytest.raises(AttributeError):
            vo.new_field = "surprise"  # type: ignore[attr-defined]

    def test_subclass_inherits_immutability(self) -> None:
        """Immutability is inherited by subclasses without re-declaration."""

        @dataclass(frozen=True)
        class Price(Money):
            """Subclass of Money."""

            vat_rate: float = 0.2

        vo = Price(50.0, "GBP")
        with pytest.raises(AttributeError):
            vo.amount = 99.0  # type: ignore[misc]
