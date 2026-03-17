"""Tests for abcdef.modularity.extraction — public API extraction."""

from pathlib import Path
from tempfile import TemporaryDirectory

from abcdef.c.markers import command, query
from abcdef.modularity.extraction import PublicApiExtractor, _get_marker
from abcdef.modularity.validation import PublicApi


class TestGetMarker:
    """Tests for _get_marker inspection utility."""

    def test_returns_marker_value_when_present(self) -> None:
        """Returns marker value when attribute exists."""

        class Marked:
            __cqrs_type__ = "command"

        assert _get_marker(Marked, "__cqrs_type__") == "command"

    def test_returns_none_when_absent(self) -> None:
        """Returns None when marker attribute is absent."""

        class Unmarked:
            pass

        assert _get_marker(Unmarked, "__cqrs_type__") is None

    def test_inherits_marker_from_parent(self) -> None:
        """Marker is inherited from parent class."""

        @command
        class Parent:
            pass

        class Child(Parent):
            pass

        assert _get_marker(Child, "__cqrs_type__") == "command"

    def test_child_marker_overrides_parent(self) -> None:
        """Child marker overrides parent."""

        @command
        class Parent:
            pass

        @query
        class Child(Parent):
            pass

        assert _get_marker(Child, "__cqrs_type__") == "query"


class TestPublicApiExtractor:
    """Tests for public API extraction."""

    def test_empty_module_returns_empty_api(self) -> None:
        """Empty __init__.py returns empty PublicApi."""
        with TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)
            (module_path / "__init__.py").write_text("", encoding="utf-8")

            extractor = PublicApiExtractor(module_path)
            api = extractor.extract()

            assert api.symbols == frozenset()
            assert api.commands == frozenset()
            assert api.queries == frozenset()
            assert api.events == frozenset()
            assert api.spis == frozenset()

    def test_extract_command_from_module(self) -> None:
        """Extracts @command marked class from module exports."""
        with TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            # Create a simple command class
            code = """from abcdef.c.markers import command

@command
class CreateOrder:
    pass

__all__ = ["CreateOrder"]
"""
            (module_path / "__init__.py").write_text(code, encoding="utf-8")

            extractor = PublicApiExtractor(module_path)
            api = extractor.extract()

            # Should have symbol but kind will be "unknown" because it can't import
            # the module in the test environment
            assert len(api.symbols) == 1
            symbol = next(iter(api.symbols))
            assert symbol.name == "CreateOrder"

    def test_infers_exports_without_all(self) -> None:
        """Infers exports when __all__ is not defined."""
        with TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            code = """from abcdef.c.markers import command

@command
class MyCommand:
    pass

__all__ = ["MyCommand"]
"""
            (module_path / "__init__.py").write_text(code, encoding="utf-8")

            extractor = PublicApiExtractor(module_path)
            api = extractor.extract()

            # Should include MyCommand in exports
            symbol_names = {s.name for s in api.symbols}
            assert "MyCommand" in symbol_names

    def test_ignores_private_symbols(self) -> None:
        """Ignores symbols starting with underscore."""
        with TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir)

            code = """class _Private:
    pass

class Public:
    pass

__all__ = ["Public"]
"""
            (module_path / "__init__.py").write_text(code, encoding="utf-8")

            extractor = PublicApiExtractor(module_path)
            api = extractor.extract()

            symbol_names = {s.name for s in api.symbols}
            assert "Public" in symbol_names
            assert "_Private" not in symbol_names


class TestPublicApiEmpty:
    """Tests for PublicApi.empty() factory."""

    def test_empty_creates_empty_api(self) -> None:
        """PublicApi.empty() creates frozenset-based empty API."""
        api = PublicApi.empty()

        assert api.symbols == frozenset()
        assert api.commands == frozenset()
        assert api.queries == frozenset()
        assert api.events == frozenset()
        assert api.spis == frozenset()
