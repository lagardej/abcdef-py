"""Integration tests for abcdef.codegen — anti-drift validation.

Generates modules into a temporary directory and validates them with
abcdef.modularity to ensure generated scaffolding never violates
the architecture rules.
"""

from pathlib import Path

from abcdef.codegen.generator import (
    ENDPOINT_API,
    ENDPOINT_WEB,
    generate_feature,
    generate_module,
)
from abcdef.modularity import Modularity
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE


class TestGeneratedCommandModuleIsValid:
    """Generated command module passes modularity validation."""

    def test_bare_command_module_has_no_violations(self, tmp_path: Path) -> None:
        """Freshly scaffolded command module has zero modularity violations."""
        generate_module("orders", COMMAND_MODULE, tmp_path)

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], (
            "Generated command module has violations:\n"
            + "\n".join(str(v) for v in violations)
        )

    def test_command_module_is_discovered(self, tmp_path: Path) -> None:
        """Generated command module is discovered by Modularity."""
        generate_module("orders", COMMAND_MODULE, tmp_path)

        modularity = Modularity(tmp_path)
        modules = modularity.discover()

        assert len(modules) == 1
        assert modules[0].declaration.module_type == COMMAND_MODULE
        assert modules[0].declaration.name == "orders"

    def test_command_module_with_feature_has_no_violations(
        self, tmp_path: Path
    ) -> None:
        """Command module with a generated feature has zero violations."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        generate_feature("orders", "create_order", tmp_path)

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], (
            "Command module with feature has violations:\n"
            + "\n".join(str(v) for v in violations)
        )


class TestGeneratedQueryModuleIsValid:
    """Generated query module passes modularity validation."""

    def test_bare_query_module_has_no_violations(self, tmp_path: Path) -> None:
        """Freshly scaffolded query module has zero modularity violations."""
        generate_module("reports", QUERY_MODULE, tmp_path)

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], "Generated query module has violations:\n" + "\n".join(
            str(v) for v in violations
        )

    def test_query_module_is_discovered(self, tmp_path: Path) -> None:
        """Generated query module is discovered by Modularity."""
        generate_module("reports", QUERY_MODULE, tmp_path)

        modularity = Modularity(tmp_path)
        modules = modularity.discover()

        assert len(modules) == 1
        assert modules[0].declaration.module_type == QUERY_MODULE
        assert modules[0].declaration.name == "reports"

    def test_query_module_with_feature_has_no_violations(self, tmp_path: Path) -> None:
        """Query module with a generated feature has zero violations."""
        generate_module("reports", QUERY_MODULE, tmp_path)
        generate_feature("reports", "list_reports", tmp_path)

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], (
            "Query module with feature has violations:\n"
            + "\n".join(str(v) for v in violations)
        )


class TestMultipleGeneratedModules:
    """Multiple generated modules coexist without violations."""

    def test_command_and_query_modules_together(self, tmp_path: Path) -> None:
        """A command module and query module scaffolded side by side are both valid."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        generate_module("reports", QUERY_MODULE, tmp_path)

        modularity = Modularity(tmp_path)
        modules = modularity.discover()
        violations = modularity.validate()

        assert len(modules) == 2
        assert violations == [], "Multiple modules have violations:\n" + "\n".join(
            str(v) for v in violations
        )


class TestGeneratedEndpointsAreValid:
    """Modules generated with non-default endpoints pass modularity validation."""

    def test_command_module_web_endpoint_has_no_violations(
        self, tmp_path: Path
    ) -> None:
        """Command module scaffolded with web endpoint has zero violations."""
        generate_module("orders", COMMAND_MODULE, tmp_path, endpoints=[ENDPOINT_WEB])

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], "Command module (web) has violations:\n" + "\n".join(
            str(v) for v in violations
        )

    def test_command_module_api_endpoint_has_no_violations(
        self, tmp_path: Path
    ) -> None:
        """Command module scaffolded with api endpoint has zero violations."""
        generate_module("orders", COMMAND_MODULE, tmp_path, endpoints=[ENDPOINT_API])

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], "Command module (api) has violations:\n" + "\n".join(
            str(v) for v in violations
        )

    def test_command_module_all_endpoints_has_no_violations(
        self, tmp_path: Path
    ) -> None:
        """Command module with all three endpoints has zero violations."""
        generate_module(
            "orders",
            COMMAND_MODULE,
            tmp_path,
            endpoints=["cli", ENDPOINT_WEB, ENDPOINT_API],
        )

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], (
            "Command module (all endpoints) has violations:\n"
            + "\n".join(str(v) for v in violations)
        )

    def test_feature_with_web_and_api_has_no_violations(self, tmp_path: Path) -> None:
        """Feature scaffolded with web and api endpoints has zero violations."""
        generate_module("orders", COMMAND_MODULE, tmp_path)
        generate_feature(
            "orders",
            "create_order",
            tmp_path,
            endpoints=[ENDPOINT_WEB, ENDPOINT_API],
        )

        modularity = Modularity(tmp_path)
        modularity.discover()
        violations = modularity.validate()

        assert violations == [], "Feature (web+api) has violations:\n" + "\n".join(
            str(v) for v in violations
        )
