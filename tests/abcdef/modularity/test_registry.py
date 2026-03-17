"""Tests for abcdef.modularity — integration and registry."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.module import ModuleDeclaration
from abcdef.modularity.registry import Modularity
from abcdef.modularity.validation import PublicApi


class TestModularityDiscovery:
    """Tests for module discovery."""

    def test_discover_no_modules_returns_empty(self) -> None:
        """No declared modules returns empty list."""
        with TemporaryDirectory() as tmpdir:
            modularity = Modularity(Path(tmpdir))
            modules = modularity.discover()

            assert modules == []

    def test_discover_command_module(self) -> None:
        """Discover a command module with __modularity__ declaration."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            # Create __init__.py with declaration
            init_code = f"""\"\"\"Order management module.\"\"\"

__modularity__ = {{
    "type": "{COMMAND_MODULE}",
    "name": "orders",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modules = modularity.discover()

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

__modularity__ = {{
    "type": "{QUERY_MODULE}",
    "name": "reports",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modules = modularity.discover()

            assert len(modules) == 1
            assert modules[0].declaration.module_type == QUERY_MODULE

    def test_extracts_docstring_as_description(self) -> None:
        """Module docstring is extracted as description."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"Handle order creation and management.\"\"\"

__modularity__ = {{
    "type": "{COMMAND_MODULE}",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modules = modularity.discover()

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

            init_code = f"""__modularity__ = {{
    "type": "{COMMAND_MODULE}",
    "name": "orders",  # logical name
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modules = modularity.discover()

            assert modules[0].declaration.name == "orders"  # logical name used
            assert modules[0].path.name == "orders_cmd"  # physical name in path

    def test_invalid_type_raises_error(self) -> None:
        """Invalid module type in declaration raises ValueError."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "invalid"
            module_dir.mkdir(parents=True)

            init_code = """__modularity__ = {
    "type": "invalid_type",
}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            with pytest.raises(ValueError, match="must be"):
                modularity.discover()

    def test_skips_test_directories(self) -> None:
        """Modules in tests/ directories are skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create app module (should be discovered)
            app_dir = root / "myapp" / "orders"
            app_dir.mkdir(parents=True)
            (app_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            # Create test module (should be skipped)
            test_dir = root / "tests" / "orders"
            test_dir.mkdir(parents=True)
            (test_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            modules = modularity.discover()

            # Only app module should be discovered
            assert len(modules) == 1

    def test_skips_venv_and_build_directories(self) -> None:
        """Modules in .venv, venv, and build directories are skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Create real app module (should be discovered)
            app_dir = root / "myapp" / "orders"
            app_dir.mkdir(parents=True)
            (app_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            # Create modules in skipped directories
            for skip_dir in (".venv", "venv", "build"):
                fake_dir = root / skip_dir / "orders"
                fake_dir.mkdir(parents=True)
                (fake_dir / "__init__.py").write_text(
                    f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                    encoding="utf-8",
                )

            modularity = Modularity(root)
            modules = modularity.discover()

            assert len(modules) == 1

    def test_skips_abcdef_packages(self) -> None:
        """Packages with 'abcdef' in their path are skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            # Module nested under an 'abcdef' path (should be skipped)
            abcdef_dir = root / "abcdef" / "orders"
            abcdef_dir.mkdir(parents=True)
            (abcdef_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            modules = modularity.discover()

            assert modules == []

    def test_skips_init_without_modularity_declaration(self) -> None:
        """__init__.py with no __modularity__ assignment is skipped."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            (module_dir / "__init__.py").write_text(
                '"""Plain package, no declaration."""\n',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            modules = modularity.discover()

            assert modules == []

    def test_missing_type_key_raises_error(self) -> None:
        """__modularity__ dict with no 'type' key raises ValueError."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            # Empty dict — no 'type' key at all
            (module_dir / "__init__.py").write_text(
                '__modularity__ = {}\n',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            with pytest.raises(ValueError, match="missing required 'type'"):
                modularity.discover()

    def test_infers_name_from_package_when_not_explicit(self) -> None:
        """Name falls back to package directory name when not set in declaration."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "billing"
            module_dir.mkdir(parents=True)

            # No 'name' key, no docstring
            (module_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}\n',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            modules = modularity.discover()

            assert modules[0].declaration.name == "billing"

    def test_explicit_description_overrides_docstring(self) -> None:
        """Explicit 'description' in __modularity__ takes precedence over docstring."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"This is the docstring.\"\"\"

__modularity__ = {{
    "type": "{COMMAND_MODULE}",
    "description": "Explicit description from dict.",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modules = modularity.discover()

            assert modules[0].declaration.description == "Explicit description from dict."


class TestCreateModuleUnknownType:
    """Tests for _create_module edge case."""

    def test_unknown_module_type_raises_value_error(self) -> None:
        """_create_module raises ValueError for an unrecognised module type."""
        decl = ModuleDeclaration(
            module_type="unknown_type",
            name="test",
            description="",
        )
        api = PublicApi.empty()

        with pytest.raises(ValueError, match="Unknown module type"):
            Modularity._create_module(decl, Path("/fake/path"), api)


class TestModularityValidation:
    """Tests for validation."""

    def test_validate_returns_empty_for_valid_modules(self) -> None:
        """No violations for valid modules."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            (module_dir / "__init__.py").write_text(
                f'__modularity__ = {{"type": "{COMMAND_MODULE}"}}',
                encoding="utf-8",
            )

            modularity = Modularity(root)
            modularity.discover()
            violations = modularity.validate()

            assert violations == []


class TestModularityDocs:
    """Tests for documentation generation."""

    def test_generate_docs_produces_markdown(self) -> None:
        """Generate docs produces valid Markdown."""
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            module_dir = root / "myapp" / "orders"
            module_dir.mkdir(parents=True)

            init_code = f"""\"\"\"Order management.\"\"\"

__modularity__ = {{
    "type": "{COMMAND_MODULE}",
}}
"""
            (module_dir / "__init__.py").write_text(init_code, encoding="utf-8")

            modularity = Modularity(root)
            modularity.discover()
            docs = modularity.generate_docs()

            assert "# Module Documentation" in docs
            assert "orders" in docs
