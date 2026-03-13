"""Tests for Value Object."""

from abcdef.core import ValueObject


class Money(ValueObject):
    """Test value object."""

    def __init__(self, amount: float, currency: str) -> None:
        """Initialise with amount and currency."""
        self.amount = amount
        self.currency = currency


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
