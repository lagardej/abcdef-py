"""Tests for abcdef.modularity.report — Markdown documentation generation."""

from pathlib import Path

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.module import (
    CommandModule,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modularity.report import MarkdownReporter
from abcdef.modularity.validation import PublicApi, PublicApiSymbol


class TestMarkdownReporter:
    """Tests for Markdown documentation generation."""

    def test_empty_modules_generates_header(self) -> None:
        """Generate docs for empty module list."""
        reporter = MarkdownReporter([])
        docs = reporter.generate()

        assert "# Module Documentation" in docs
        assert "Modules" in docs

    def test_single_command_module_documented(self) -> None:
        """Document a single command module."""
        cmd = PublicApiSymbol("CreateOrder", "command", "orders.CreateOrder")
        evt = PublicApiSymbol("OrderCreated", "event", "orders.OrderCreated")

        api = PublicApi(
            symbols=frozenset([cmd, evt]),
            commands=frozenset([cmd]),
            queries=frozenset(),
            events=frozenset([evt]),
            spis=frozenset(),
        )

        decl = ModuleDeclaration(
            module_type=COMMAND_MODULE,
            name="orders",
            description="Order management system",
        )

        module = CommandModule(
            _declaration=decl, _path=Path("/app/orders"), _public_api=api
        )

        reporter = MarkdownReporter([module])
        docs = reporter.generate()

        assert "orders" in docs
        assert "Order management system" in docs
        assert "command module" in docs.lower()
        assert "CreateOrder" in docs
        assert "OrderCreated" in docs

    def test_single_query_module_documented(self) -> None:
        """Document a single query module."""
        qry = PublicApiSymbol("GetOrders", "query", "orders_reports.GetOrders")

        api = PublicApi(
            symbols=frozenset([qry]),
            commands=frozenset(),
            queries=frozenset([qry]),
            events=frozenset(),
            spis=frozenset(),
        )

        decl = ModuleDeclaration(
            module_type=QUERY_MODULE,
            name="orders_reports",
            description="Order reporting and analytics",
        )

        module = QueryModule(
            _declaration=decl,
            _path=Path("/app/orders_reports"),
            _public_api=api,
        )

        reporter = MarkdownReporter([module])
        docs = reporter.generate()

        assert "orders_reports" in docs
        assert "query module" in docs.lower()
        assert "GetOrders" in docs

    def test_multiple_modules_listed_in_toc(self) -> None:
        """Table of contents lists all modules."""
        m1 = CommandModule(
            _declaration=ModuleDeclaration(COMMAND_MODULE, "orders"),
            _path=Path("/app/orders"),
            _public_api=PublicApi.empty(),
        )
        m2 = QueryModule(
            _declaration=ModuleDeclaration(QUERY_MODULE, "reports"),
            _path=Path("/app/reports"),
            _public_api=PublicApi.empty(),
        )

        reporter = MarkdownReporter([m2, m1])  # reversed order
        docs = reporter.generate()

        # Should be sorted by name
        idx_orders = docs.index("orders")
        idx_reports = docs.index("reports")
        assert idx_orders < idx_reports

    def test_spi_symbols_documented(self) -> None:
        """Document Service Provider Interfaces."""
        spi = PublicApiSymbol("OrderRepository", "spi", "orders.OrderRepository")

        api = PublicApi(
            symbols=frozenset([spi]),
            commands=frozenset(),
            queries=frozenset(),
            events=frozenset(),
            spis=frozenset([spi]),
        )

        decl = ModuleDeclaration(COMMAND_MODULE, "orders")
        module = CommandModule(
            _declaration=decl,
            _path=Path("/app/orders"),
            _public_api=api,
        )

        reporter = MarkdownReporter([module])
        docs = reporter.generate()

        assert "Service Provider Interface" in docs or "SPI" in docs
        assert "OrderRepository" in docs

    def test_omits_internal_details(self) -> None:
        """Documentation does not mention internal layer structure."""
        decl = ModuleDeclaration(COMMAND_MODULE, "orders")
        module = CommandModule(
            _declaration=decl,
            _path=Path("/app/orders"),
            _public_api=PublicApi.empty(),
        )

        reporter = MarkdownReporter([module])
        docs = reporter.generate()

        # Should not mention internal layers
        assert "domain/" not in docs.lower()
        assert "infrastructure/" not in docs.lower()
        assert "projection/" not in docs.lower()
