"""Tests for abcdef.modulith — integration and registry."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from abcdef.modulith.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modulith.registry import Modulith


class TestModulithDiscovery:
    """Tests for module discovery."""

    def test_discover_no_modules_returns_empty(self) -> None:
        """No declared modules returns empty list."""
        with TemporaryDirectory() as tmpdir:
            modulith = Modulith(Path(tmpdir))
            modules = modulith.discover()

            assert modules == []

    def test_discover_command_module(self) -> None:
        """Discover a command module with __modulith__ declaration."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            # Create __init__.py with declaration
            init_code = f"""\"\"\"Order management module.\"\"\"

__modulith__ = {{
    "type": "{COMMAND_MODULE}",
    "name": "orders",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            modules = modulith.discover()

            assert len(modules) == 1
            module = modules[0]
            assert module.declaration.module_type == COMMAND_MODULE
            assert module.declaration.name == "orders"

    def test_discover_query_module(self) -> None:
        """Discover a query module."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "reports"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"Reporting module.\"\"\"

__modulith__ = {{
    "type": "{QUERY_MODULE}",
    "name": "reports",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            modules = modulith.discover()

            assert len(modules) == 1
            assert modules[0].declaration.module_type == QUERY_MODULE

    def test_extracts_docstring_as_description(self) -> None:
        """Module docstring is extracted as description."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"Handle order creation and management.\"\"\"

__modulith__ = {{
    "type": "{COMMAND_MODULE}",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            modules = modulith.discover()

            assert (
                modules[0].declaration.description
                == "Handle order creation and management."
            )

    def test_explicit_name_overrides_package_name(self) -> None:
        """Explicit 'name' in declaration overrides package name."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders_cmd"  # physical name
            module_dir.mkdir(parents=True)

            init_code = f"""__modulith__ = {{
    "type": "{COMMAND_MODULE}",
    "name": "orders",  # logical name
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            modules = modulith.discover()

            assert modules[0].declaration.name == "orders"  # logical name used
            assert modules[0].path.name == "orders_cmd"  # physical name in path

    def test_invalid_type_raises_error(self) -> None:
        """Invalid module type in declaration raises ValueError."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "invalid"
            module_dir.mkdir(parents=True)

            init_code = """__modulith__ = {
    "type": "invalid_type",
}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            with pytest.raises(ValueError, match="must be"):
                modulith.discover()

    def test_skips_test_directories(self) -> None:
        """Modules in tests/ directories are skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create app module (should be discovered)
            app_dir = root / "myapp" / "orders"
            app_dir.mkdir(parents=True)
            (app_dir / "__init__.py").write_text(
                f'__modulith__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            # Create test module (should be skipped)
            test_dir = root / "tests" / "orders"
            test_dir.mkdir(parents=True)
            (test_dir / "__init__.py").write_text(
                f'__modulith__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            modulith = Modulith(root)
            modules = modulith.discover()

            # Only app module should be discovered
            assert len(modules) == 1


class TestModulithValidation:
    """Tests for validation."""

    def test_validate_returns_empty_for_valid_modules(self) -> None:
        """No violations for valid modules."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            (module_dir / "__init__.py").write_text(
                f'__modulith__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            modulith = Modulith(root)
            modulith.discover()
            violations = modulith.validate()

            assert violations == []


class TestModulithDocs:
    """Tests for documentation generation."""

    def test_generate_docs_produces_markdown(self) -> None:
        """Generate docs produces valid Markdown."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"Order management.\"\"\"

__modulith__ = {{
    "type": "{COMMAND_MODULE}",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modulith = Modulith(root)
            modulith.discover()
            docs = modulith.generate_docs()

            assert "# Module Documentation" in docs
            assert "orders" in docs
