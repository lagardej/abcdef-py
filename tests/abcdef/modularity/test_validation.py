"""Tests for abcdef.modularity.validation — violation detection."""

import pytest

from abcdef.modularity.validation import PublicApi, PublicApiSymbol, Violation


class TestViolation:
    """Tests for Violation dataclass."""

    def test_create_violation(self) -> None:
        """Create a violation record."""
        vio = Violation(
            module_name="orders",
            violation_type="read_write_constraint",
            message="Command module exports queries",
            location="orders/__init__.py",
        )

        assert vio.module_name == "orders"
        assert vio.violation_type == "read_write_constraint"
        assert vio.message == "Command module exports queries"
        assert vio.location == "orders/__init__.py"

    def test_violation_location_optional(self) -> None:
        """Location is optional."""
        vio = Violation(
            module_name="orders",
            violation_type="test",
            message="Test violation",
        )

        assert vio.location is None

    def test_violation_is_frozen(self) -> None:
        """Violation is immutable."""
        vio = Violation(
            module_name="orders",
            violation_type="test",
            message="Test",
        )

        with pytest.raises(AttributeError):
            vio.module_name = "changed"  # type: ignore[misc]


class TestPublicApiSymbol:
    """Tests for PublicApiSymbol dataclass."""

    def test_create_symbol(self) -> None:
        """Create a public API symbol."""
        symbol = PublicApiSymbol(
            name="CreateOrder",
            kind="command",
            full_path="myapp.orders.commands.CreateOrder",
        )

        assert symbol.name == "CreateOrder"
        assert symbol.kind == "command"
        assert symbol.full_path == "myapp.orders.commands.CreateOrder"

    def test_symbol_is_frozen(self) -> None:
        """PublicApiSymbol is immutable."""
        symbol = PublicApiSymbol(name="CreateOrder", kind="command", full_path="...")

        with pytest.raises(AttributeError):
            symbol.kind = "query"  # type: ignore[misc]


class TestPublicApi:
    """Tests for PublicApi dataclass."""

    def test_create_public_api(self) -> None:
        """Create public API with symbols."""
        cmd = PublicApiSymbol("CreateOrder", "command", "...")
        qry = PublicApiSymbol("GetOrders", "query", "...")
        evt = PublicApiSymbol("OrderCreated", "event", "...")
        spi = PublicApiSymbol("OrderRepository", "spi", "...")

        api = PublicApi(
            symbols=frozenset([cmd, qry, evt, spi]),
            commands=frozenset([cmd]),
            queries=frozenset([qry]),
            events=frozenset([evt]),
            spis=frozenset([spi]),
        )

        assert len(api.symbols) == 4
        assert len(api.commands) == 1
        assert len(api.queries) == 1
        assert len(api.events) == 1
        assert len(api.spis) == 1

    def test_empty_public_api(self) -> None:
        """Create empty PublicApi."""
        api = PublicApi.empty()

        assert api.symbols == frozenset()
        assert api.commands == frozenset()
        assert api.queries == frozenset()
        assert api.events == frozenset()
        assert api.spis == frozenset()
