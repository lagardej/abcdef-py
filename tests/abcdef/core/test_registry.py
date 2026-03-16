"""Tests for ClassRegistry."""

import pytest

from abcdef.core.registry import ClassRegistry


class _Base:
    """Minimal base class for registry tests."""


class _ConcreteA(_Base):
    """First concrete subclass."""


class _ConcreteB(_Base):
    """Second concrete subclass."""


class TestClassRegistry:
    """Tests for ClassRegistry contract."""

    def test_register_and_get(self) -> None:
        """A registered class is retrievable by key."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        registry.register("a", _ConcreteA)
        assert registry.get("a") is _ConcreteA

    def test_get_unknown_key_raises(self) -> None:
        """Looking up an unregistered key raises KeyError."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        with pytest.raises(KeyError):
            registry.get("no_such_key")

    def test_duplicate_key_raises(self) -> None:
        """Registering the same key twice raises TypeError."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        registry.register("a", _ConcreteA)
        with pytest.raises(TypeError, match="already registered"):
            registry.register("a", _ConcreteB)

    def test_duplicate_error_includes_key(self) -> None:
        """TypeError message includes the duplicate key."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        registry.register("my_key", _ConcreteA)
        with pytest.raises(TypeError, match="my_key"):
            registry.register("my_key", _ConcreteB)

    def test_duplicate_error_includes_existing_class(self) -> None:
        """TypeError message names the class already holding the key."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        registry.register("a", _ConcreteA)
        with pytest.raises(TypeError, match="_ConcreteA"):
            registry.register("a", _ConcreteB)

    def test_multiple_keys_are_independent(self) -> None:
        """Multiple keys can be registered and retrieved independently."""
        registry: ClassRegistry[type[_Base]] = ClassRegistry()
        registry.register("a", _ConcreteA)
        registry.register("b", _ConcreteB)
        assert registry.get("a") is _ConcreteA
        assert registry.get("b") is _ConcreteB

    def test_each_instance_is_independent(self) -> None:
        """Two registry instances do not share state."""
        r1: ClassRegistry[type[_Base]] = ClassRegistry()
        r2: ClassRegistry[type[_Base]] = ClassRegistry()
        r1.register("a", _ConcreteA)
        with pytest.raises(KeyError):
            r2.get("a")
