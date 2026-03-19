"""Tests for abcdef.codegen.generator — unit tests."""

from pathlib import Path

import pytest

from abcdef.codegen.generator import (
    ENTRYPOINT_API,
    ENTRYPOINT_CLI,
    ENTRYPOINT_WEB,
    _to_pascal,
    generate_feature,
    generate_module,
)
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE


class TestToPascal:
    """Tests for _to_pascal helper."""

    def test_single_word(self) -> None:
        """Single word is capitalised."""
        assert _to_pascal("orders") == "Orders"

    def test_snake_case(self) -> None:
        """Snake case is converted to PascalCase."""
        assert _to_pascal("create_order") == "CreateOrder"

    def test_multiple_words(self) -> None:
        """Multiple underscore-separated words."""
        assert _to_pascal("get_order_by_id") == "GetOrderById"


class TestGenerateModule:
    """Tests for generate_module()."""

    def test_command_module_creates_expected_files(self, tmp_path: Path) -> None:
        """Command module scaffold creates all expected files."""
        created = generate_module("orders", COMMAND_MODULE, tmp_path)

        rel = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("__init__.py") in rel
        assert Path("domain/orders.py") in rel
        assert Path("domain/orders_repository.py") in rel
        assert Path("application/placeholder.py") in rel
        assert Path("infrastructure/placeholder.py") in rel
        assert Path("entrypoint/cli/placeholder.py") in rel

    def test_query_module_creates_expected_files(self, tmp_path: Path) -> None:
        """Query module scaffold creates all expected files."""
        created = generate_module("reports", QUERY_MODULE, tmp_path)

        rel = {p.relative_to(tmp_path / "reports") for p in created}
        assert Path("__init__.py") in rel
        assert Path("projection/reports.py") in rel
        assert Path("application/placeholder.py") in rel
        assert Path("infrastructure/placeholder.py") in rel
        assert Path("entrypoint/cli/placeholder.py") in rel

    def test_command_init_contains_modularity_dict(self, tmp_path: Path) -> None:
        """Generated __init__.py contains __modularity__ dict with COMMAND_MODULE."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        init = (tmp_path / "orders" / "__init__.py").read_text(encoding="utf-8")

        assert "__modularity__" in init
        assert COMMAND_MODULE in init
        assert "__all__" in init

    def test_query_init_contains_modularity_dict(self, tmp_path: Path) -> None:
        """Generated __init__.py contains __modularity__ dict with QUERY_MODULE."""
        generate_module("reports", QUERY_MODULE, tmp_path)
        init = (tmp_path / "reports" / "__init__.py").read_text(encoding="utf-8")

        assert "__modularity__" in init
        assert QUERY_MODULE in init

    def test_module_name_substituted_in_init(self, tmp_path: Path) -> None:
        """Module name is substituted correctly in __init__.py."""
        generate_module("billing", COMMAND_MODULE, tmp_path)
        init = (tmp_path / "billing" / "__init__.py").read_text(encoding="utf-8")

        assert "billing" in init
        assert "Billing" in init

    def test_aggregate_file_contains_pascal_class(self, tmp_path: Path) -> None:
        """Aggregate file uses PascalCase class name derived from module name."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        aggregate = (tmp_path / "orders" / "domain" / "orders.py").read_text(
            encoding="utf-8"
        )

        assert "class Orders(" in aggregate
        assert "class OrdersId(" in aggregate

    def test_query_document_file_contains_pascal_class(self, tmp_path: Path) -> None:
        """Document file uses PascalCase class name derived from module name."""
        generate_module("reports", QUERY_MODULE, tmp_path)
        doc = (tmp_path / "reports" / "projection" / "reports.py").read_text(
            encoding="utf-8"
        )

        assert "class ReportsDocument(" in doc

    def test_refuses_if_directory_exists(self, tmp_path: Path) -> None:
        """Raises FileExistsError if module directory already exists."""
        (tmp_path / "orders").mkdir()

        with pytest.raises(FileExistsError, match="already exists"):
            generate_module("orders", COMMAND_MODULE, tmp_path)

    def test_raises_for_invalid_module_type(self, tmp_path: Path) -> None:
        """Raises ValueError for unrecognised module type."""
        with pytest.raises(ValueError, match="module_type must be"):
            generate_module("orders", "invalid", tmp_path)

    def test_returns_list_of_paths(self, tmp_path: Path) -> None:
        """Return value is a non-empty list of Path objects."""
        created = generate_module("orders", COMMAND_MODULE, tmp_path)

        assert isinstance(created, list)
        assert len(created) > 0
        assert all(isinstance(p, Path) for p in created)
        assert all(p.exists() for p in created)

    def test_snake_case_module_name(self, tmp_path: Path) -> None:
        """Multi-word snake_case module names are handled correctly."""
        generate_module("order_management", COMMAND_MODULE, tmp_path)

        init = (tmp_path / "order_management" / "__init__.py").read_text(
            encoding="utf-8"
        )
        assert "order_management" in init
        assert "OrderManagement" in init


class TestGenerateFeature:
    """Tests for generate_feature()."""

    def _scaffold_command_module(self, root: Path, name: str = "orders") -> None:
        """Helper: scaffold a minimal command module for feature tests."""
        generate_module(name, COMMAND_MODULE, root)

    def _scaffold_query_module(self, root: Path, name: str = "reports") -> None:
        """Helper: scaffold a minimal query module for feature tests."""
        generate_module(name, QUERY_MODULE, root)

    def test_command_feature_creates_application_file(self, tmp_path: Path) -> None:
        """Feature adds application/<use_case>.py for a command module."""
        self._scaffold_command_module(tmp_path)
        generate_feature("orders", "create_order", tmp_path)

        assert (tmp_path / "orders" / "application" / "create_order.py").exists()

    def test_command_feature_creates_cli_file(self, tmp_path: Path) -> None:
        """Feature adds entrypoint/cli/<use_case>.py for a command module."""
        self._scaffold_command_module(tmp_path)
        generate_feature("orders", "create_order", tmp_path)

        assert (tmp_path / "orders" / "entrypoint" / "cli" / "create_order.py").exists()

    def test_query_feature_creates_application_file(self, tmp_path: Path) -> None:
        """Feature adds application/<use_case>.py for a query module."""
        self._scaffold_query_module(tmp_path)
        generate_feature("reports", "get_report", tmp_path)

        assert (tmp_path / "reports" / "application" / "get_report.py").exists()

    def test_query_feature_creates_cli_file(self, tmp_path: Path) -> None:
        """Feature adds entrypoint/cli/<use_case>.py for a query module."""
        self._scaffold_query_module(tmp_path)
        generate_feature("reports", "get_report", tmp_path)

        assert (tmp_path / "reports" / "entrypoint" / "cli" / "get_report.py").exists()

    def test_command_feature_content_has_correct_class_names(
        self, tmp_path: Path
    ) -> None:
        """Command feature file contains correct PascalCase class names."""
        self._scaffold_command_module(tmp_path)
        generate_feature("orders", "create_order", tmp_path)

        content = (tmp_path / "orders" / "application" / "create_order.py").read_text(
            encoding="utf-8"
        )

        assert "class CreateOrder(" in content
        assert "class CreateOrderHandler(" in content

    def test_query_feature_content_has_correct_class_names(
        self, tmp_path: Path
    ) -> None:
        """Query feature file contains correct PascalCase class names."""
        self._scaffold_query_module(tmp_path)
        generate_feature("reports", "get_report", tmp_path)

        content = (tmp_path / "reports" / "application" / "get_report.py").read_text(
            encoding="utf-8"
        )

        assert "class GetReport(" in content
        assert "class GetReportHandler(" in content

    def test_does_not_modify_init(self, tmp_path: Path) -> None:
        """generate_feature does not touch __init__.py."""
        self._scaffold_command_module(tmp_path)
        init_before = (tmp_path / "orders" / "__init__.py").read_text(encoding="utf-8")

        generate_feature("orders", "create_order", tmp_path)

        init_after = (tmp_path / "orders" / "__init__.py").read_text(encoding="utf-8")
        assert init_before == init_after

    def test_refuses_if_module_dir_missing(self, tmp_path: Path) -> None:
        """Raises FileNotFoundError if module directory does not exist."""
        with pytest.raises(FileNotFoundError, match="Module directory not found"):
            generate_feature("orders", "create_order", tmp_path)

    def test_refuses_if_application_file_exists(self, tmp_path: Path) -> None:
        """Raises FileExistsError if application file already exists."""
        self._scaffold_command_module(tmp_path)
        generate_feature("orders", "create_order", tmp_path)

        with pytest.raises(FileExistsError, match="already exists"):
            generate_feature("orders", "create_order", tmp_path)

    def test_returns_list_of_created_paths(self, tmp_path: Path) -> None:
        """Return value is a list of two Path objects that exist."""
        self._scaffold_command_module(tmp_path)
        created = generate_feature("orders", "create_order", tmp_path)

        assert len(created) == 2
        assert all(isinstance(p, Path) for p in created)
        assert all(p.exists() for p in created)

    def test_infers_query_type_from_init(self, tmp_path: Path) -> None:
        """generate_feature uses Query template when module type is QUERY_MODULE."""
        self._scaffold_query_module(tmp_path)
        generate_feature("reports", "list_reports", tmp_path)

        content = (tmp_path / "reports" / "application" / "list_reports.py").read_text(
            encoding="utf-8"
        )

        assert "Query" in content
        assert "QueryHandler" in content

    def test_feature_without_init_modularity_raises(self, tmp_path: Path) -> None:
        """Raises ValueError if __init__.py has no __modularity__ dict."""
        module_dir = tmp_path / "orders"
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text(
            '"""No modularity declaration."""\n', encoding="utf-8"
        )

        with pytest.raises(ValueError, match="no __modularity__ declaration"):
            generate_feature("orders", "create_order", tmp_path)


class TestEntrypoints:
    """Tests for --entrypoints parameter on generate_module and generate_feature."""

    def test_module_default_entrypoint_is_cli(self, tmp_path: Path) -> None:
        """Default entrypoint is cli when entrypoints is not specified."""
        created = generate_module("orders", COMMAND_MODULE, tmp_path)

        rel = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/cli/placeholder.py") in rel
        assert not any("web" in str(p) for p in rel)
        assert not any("api" in str(p) for p in rel)

    def test_module_web_entrypoint(self, tmp_path: Path) -> None:
        """Web entrypoint generates entrypoint/web/placeholder.py."""
        created = generate_module(
            "orders", COMMAND_MODULE, tmp_path, entrypoints=[ENTRYPOINT_WEB]
        )

        rel = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/web/placeholder.py") in rel
        assert not any("cli" in str(p) for p in rel)

    def test_module_api_entrypoint(self, tmp_path: Path) -> None:
        """API entrypoint generates entrypoint/api/placeholder.py."""
        created = generate_module(
            "orders", COMMAND_MODULE, tmp_path, entrypoints=[ENTRYPOINT_API]
        )

        rel = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/api/placeholder.py") in rel
        assert not any("cli" in str(p) for p in rel)

    def test_module_multiple_entrypoints(self, tmp_path: Path) -> None:
        """Multiple entrypoints each generate their own stub."""
        created = generate_module(
            "orders",
            COMMAND_MODULE,
            tmp_path,
            entrypoints=[ENTRYPOINT_CLI, ENTRYPOINT_WEB, ENTRYPOINT_API],
        )

        rel = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/cli/placeholder.py") in rel
        assert Path("entrypoint/web/placeholder.py") in rel
        assert Path("entrypoint/api/placeholder.py") in rel

    def test_module_invalid_entrypoint_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for unrecognised entrypoint name."""
        with pytest.raises(ValueError, match="Unknown entrypoint"):
            generate_module("orders", COMMAND_MODULE, tmp_path, entrypoints=["graphql"])

    def test_query_module_web_entrypoint(self, tmp_path: Path) -> None:
        """Web entrypoint works for query modules."""
        created = generate_module(
            "reports", QUERY_MODULE, tmp_path, entrypoints=[ENTRYPOINT_WEB]
        )

        rel = {p.relative_to(tmp_path / "reports") for p in created}
        assert Path("entrypoint/web/placeholder.py") in rel

    def test_query_module_api_entrypoint(self, tmp_path: Path) -> None:
        """API entrypoint works for query modules."""
        created = generate_module(
            "reports", QUERY_MODULE, tmp_path, entrypoints=[ENTRYPOINT_API]
        )

        rel = {p.relative_to(tmp_path / "reports") for p in created}
        assert Path("entrypoint/api/placeholder.py") in rel

    def test_feature_default_entrypoint_is_cli(self, tmp_path: Path) -> None:
        """Feature default entrypoint is cli."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        created = generate_feature("orders", "create_order", tmp_path)

        assert any("cli" in str(p) for p in created)
        assert not any("web" in str(p) for p in created)

    def test_feature_web_entrypoint(self, tmp_path: Path) -> None:
        """Feature generates entrypoint/web/<use_case>.py for web entrypoint."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        created = generate_feature(
            "orders", "create_order", tmp_path, entrypoints=[ENTRYPOINT_WEB]
        )

        paths = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/web/create_order.py") in paths

    def test_feature_api_entrypoint(self, tmp_path: Path) -> None:
        """Feature generates entrypoint/api/<use_case>.py for api entrypoint."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        created = generate_feature(
            "orders", "create_order", tmp_path, entrypoints=[ENTRYPOINT_API]
        )

        paths = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/api/create_order.py") in paths

    def test_feature_multiple_entrypoints(self, tmp_path: Path) -> None:
        """Feature with multiple entrypoints creates one file per entrypoint."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        created = generate_feature(
            "orders",
            "create_order",
            tmp_path,
            entrypoints=[ENTRYPOINT_CLI, ENTRYPOINT_WEB, ENTRYPOINT_API],
        )

        # application file + 3 entrypoint files
        assert len(created) == 4
        paths = {p.relative_to(tmp_path / "orders") for p in created}
        assert Path("entrypoint/cli/create_order.py") in paths
        assert Path("entrypoint/web/create_order.py") in paths
        assert Path("entrypoint/api/create_order.py") in paths

    def test_feature_invalid_entrypoint_raises(self, tmp_path: Path) -> None:
        """Raises ValueError for unrecognised entrypoint name in feature."""
        generate_module("orders", COMMAND_MODULE, tmp_path)

        with pytest.raises(ValueError, match="Unknown entrypoint"):
            generate_feature(
                "orders", "create_order", tmp_path, entrypoints=["graphql"]
            )

    def test_web_template_content_mentions_html(self, tmp_path: Path) -> None:
        """Web entrypoint stub mentions HTML in its docstring."""
        generate_module(
            "orders", COMMAND_MODULE, tmp_path, entrypoints=[ENTRYPOINT_WEB]
        )
        content = (
            tmp_path / "orders" / "entrypoint" / "web" / "placeholder.py"
        ).read_text(encoding="utf-8")

        assert "HTML" in content or "template" in content.lower()

    def test_api_template_content_mentions_json(self, tmp_path: Path) -> None:
        """API entrypoint stub mentions JSON in its docstring."""
        generate_module(
            "orders", COMMAND_MODULE, tmp_path, entrypoints=[ENTRYPOINT_API]
        )
        content = (
            tmp_path / "orders" / "entrypoint" / "api" / "placeholder.py"
        ).read_text(encoding="utf-8")

        assert "JSON" in content
