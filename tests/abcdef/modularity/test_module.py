"""Tests for abcdef.modularity.module — module types."""

from pathlib import Path

import pytest

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.module import (
    CommandModule,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modularity.validation import PublicApi


class TestModuleDeclaration:
    """Tests for ModuleDeclaration dataclass."""

    def test_create_command_module_declaration(self) -> None:
        """Create command module declaration."""
        decl = ModuleDeclaration(
            module_type=COMMAND_MODULE,
            name="orders",
            description="Order management",
        )

        assert decl.module_type == COMMAND_MODULE
        assert decl.name == "orders"
        assert decl.description == "Order management"

    def test_create_query_module_declaration(self) -> None:
        """Create query module declaration."""
        decl = ModuleDeclaration(module_type=QUERY_MODULE, name="reports")

        assert decl.module_type == QUERY_MODULE
        assert decl.name == "reports"
        assert decl.description == ""

    def test_declaration_is_frozen(self) -> None:
        """ModuleDeclaration is immutable."""
        decl = ModuleDeclaration(module_type=COMMAND_MODULE, name="test")

        with pytest.raises(AttributeError):
            decl.name = "changed"  # type: ignore[misc]


class TestCommandModule:
    """Tests for CommandModule type."""

    def test_create_command_module(self) -> None:
        """Create CommandModule instance."""
        decl = ModuleDeclaration(module_type=COMMAND_MODULE, name="orders")
        path = Path("/app/orders")
        api = PublicApi.empty()

        module = CommandModule(_declaration=decl, _path=path, _public_api=api)

        assert module.declaration == decl
        assert module.path == path
        assert module.public_api == api

    def test_command_module_requires_correct_type(self) -> None:
        """CommandModule constructor enforces module_type."""
        decl = ModuleDeclaration(module_type=QUERY_MODULE, name="orders")
        path = Path("/app/orders")
        api = PublicApi.empty()

        with pytest.raises(ValueError, match="CommandModule requires"):
            CommandModule(_declaration=decl, _path=path, _public_api=api)

    def test_command_module_is_frozen(self) -> None:
        """CommandModule is immutable."""
        decl = ModuleDeclaration(module_type=COMMAND_MODULE, name="orders")
        module = CommandModule(
            _declaration=decl,
            _path=Path("/app/orders"),
            _public_api=PublicApi.empty(),
        )

        with pytest.raises(AttributeError):
            module.declaration = ModuleDeclaration(  # type: ignore[misc]
                module_type=COMMAND_MODULE, name="changed"
            )


class TestQueryModule:
    """Tests for QueryModule type."""

    def test_create_query_module(self) -> None:
        """Create QueryModule instance."""
        decl = ModuleDeclaration(module_type=QUERY_MODULE, name="reports")
        path = Path("/app/reports")
        api = PublicApi.empty()

        module = QueryModule(_declaration=decl, _path=path, _public_api=api)

        assert module.declaration == decl
        assert module.path == path
        assert module.public_api == api

    def test_query_module_requires_correct_type(self) -> None:
        """QueryModule constructor enforces module_type."""
        decl = ModuleDeclaration(module_type=COMMAND_MODULE, name="reports")
        path = Path("/app/reports")
        api = PublicApi.empty()

        with pytest.raises(ValueError, match="QueryModule requires"):
            QueryModule(_declaration=decl, _path=path, _public_api=api)
