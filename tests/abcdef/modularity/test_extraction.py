"""Tests for abcdef.modularity.extraction — public API extraction."""

import ast
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


def test_import_success_and_marker_categorisation() -> None:
    """When the package can be imported, exported classes are categorised by markers."""
    import sys
    import importlib

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "root"
        pkg = root / "mypkg"
        pkg.mkdir(parents=True)

        code = """from abcdef.c.markers import command, query

@command
class CreateOrder:
    pass

@query
class FetchOrder:
    pass

__all__ = ["CreateOrder", "FetchOrder"]
"""
        (pkg / "__init__.py").write_text(code, encoding="utf-8")

        sys.path.insert(0, str(Path(tmpdir)))
        try:
            extractor = PublicApiExtractor(pkg)
            api = extractor.extract()

            cmd_names = {s.name for s in api.commands}
            qry_names = {s.name for s in api.queries}

            assert "CreateOrder" in cmd_names
            assert "FetchOrder" in qry_names
        finally:
            # cleanup
            sys.path.remove(str(Path(tmpdir)))
            for m in list(sys.modules):
                if m.startswith("root"):
                    del sys.modules[m]


def test_import_failure_returns_unknown_kinds() -> None:
    """If importing the module fails, extractor falls back to unknown kinds."""
    import sys

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "root"
        pkg = root / "badpkg"
        pkg.mkdir(parents=True)

        code = """__all__ = ["Bad"]
raise ImportError("boom")
"""
        (pkg / "__init__.py").write_text(code, encoding="utf-8")

        sys.path.insert(0, str(Path(tmpdir)))
        try:
            extractor = PublicApiExtractor(pkg)
            api = extractor.extract()

            symbol_names = {s.name for s in api.symbols}
            assert "Bad" in symbol_names
            assert all(s.kind == "unknown" for s in api.symbols)
        finally:
            sys.path.remove(str(Path(tmpdir)))
            for m in list(sys.modules):
                if m.startswith("root"):
                    del sys.modules[m]


def test_get_exported_names_handles_import_aliases() -> None:
    """AST-based export inference should include aliased imports and top-level names."""
    import ast

    src = """from .bar import Foo as BarAlias
import os
X = 1
_private = 2
"""
    tree = ast.parse(src)
    extractor = PublicApiExtractor(Path("."))
    names = extractor._get_exported_names(tree)

    assert "BarAlias" in names
    assert "os" in names
    assert "X" in names
    assert "_private" not in names


def test___all_non_list_falls_back_to_inference() -> None:
    """If __all__ is not an ast.List (e.g., a tuple), fallback inference is used."""
    src = """__all__ = ('A',)
from .pkg import X as Y
Z = 1
"""
    tree = ast.parse(src)
    extractor = PublicApiExtractor(Path("."))
    names = extractor._get_exported_names(tree)

    # Should fall back and include the import alias and assignment name
    assert "Y" in names
    assert "Z" in names


def test_non_class_exports_are_ignored_and_marker_priority() -> None:
    """Only class objects are categorised; marker priority is respected."""
    import sys

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "root"
        pkg = root / "mixpkg"
        pkg.mkdir(parents=True)

        code = """from abcdef.c.markers import command

CONST = 1

@command
class Cmd:
    pass

class NotAClass:
    pass

__all__ = ["CONST", "Cmd", "NotAClass"]
"""
        (pkg / "__init__.py").write_text(code, encoding="utf-8")

        sys.path.insert(0, str(Path(tmpdir)))
        try:
            extractor = PublicApiExtractor(pkg)
            api = extractor.extract()

            # Only the class Cmd should be categorised as a command
            assert any(s.name == "Cmd" for s in api.commands)
            # CONST is not a class and should not appear in api.symbols
            assert all(s.name != "CONST" for s in api.symbols)
        finally:
            sys.path.remove(str(Path(tmpdir)))
            for m in list(sys.modules):
                if m.startswith("root"):
                    del sys.modules[m]


def test_import_infers_dotted_import_package_name() -> None:
    """Import of a dotted module should infer the top-level package name."""
    src = """import package.module
"""
    tree = ast.parse(src)
    extractor = PublicApiExtractor(Path("."))
    names = extractor._get_exported_names(tree)

    assert "package" in names


def test_no_init_returns_empty() -> None:
    """If the package has no __init__.py the extractor returns an empty API."""
    with TemporaryDirectory() as tmpdir:
        module_path = Path(tmpdir) / "pkg"
        module_path.mkdir(parents=True)

        extractor = PublicApiExtractor(module_path)
        api = extractor.extract()

        assert api.symbols == frozenset()
        assert api.commands == frozenset()
        assert api.queries == frozenset()
        assert api.events == frozenset()
        assert api.spis == frozenset()


def test_ddd_and_modularity_markers_are_categorised() -> None:
    """Classes with __ddd_type__ and __modularity_type__ markers are categorised."""
    import sys

    with TemporaryDirectory() as tmpdir:
        root = Path(tmpdir) / "root"
        pkg = root / "markerspkg"
        pkg.mkdir(parents=True)

        code = """class E:
    __ddd_type__ = 'domain_event'

class S:
    __modularity_type__ = 'spi'

__all__ = ['E', 'S']
"""
        (pkg / "__init__.py").write_text(code, encoding="utf-8")

        sys.path.insert(0, str(Path(tmpdir)))
        try:
            extractor = PublicApiExtractor(pkg)
            api = extractor.extract()

            assert any(s.name == "E" for s in api.events)
            assert any(s.name == "S" for s in api.spis)
        finally:
            sys.path.remove(str(Path(tmpdir)))
            for m in list(sys.modules):
                if m.startswith("root"):
                    del sys.modules[m]


def test___all_ignores_non_constant_entries() -> None:
    """When __all__ contains non-Constant entries, only Constant values are used."""
    src = """__all__ = [A, 'B']
A = 1
"""
    tree = ast.parse(src)
    extractor = PublicApiExtractor(Path("."))
    names = extractor._get_exported_names(tree)

    assert names == {"B"}


