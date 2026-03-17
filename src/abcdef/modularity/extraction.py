"""Public API extraction from module root exports.

Uses AST analysis to discover exported symbols and marker inspection to
categorise them.
"""

from __future__ import annotations

import ast
import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from pathlib import Path
    from types import ModuleType

    from abcdef.modularity.validation import PublicApi, PublicApiSymbol


def _get_marker(cls: type, marker_attr: str) -> str | None:
    """Get marker value from class or its parents.

    Args:
        cls: The class to inspect.
        marker_attr: The marker attribute name (``__cqrs_type__``, ``__ddd_type__``,
            ``__de_type__``, ``__modularity_type__``, or ``__specification_type__``).

    Returns:
        The marker value if found on the class or any base class, None otherwise.
    """
    value = getattr(cls, marker_attr, None)
    return cast("str", value) if value is not None else None


class PublicApiExtractor:
    """Extracts public API of a module by inspecting its root `__init__.py`.

    Uses AST analysis to discover exports and marker inspection to categorise
    symbols.
    """

    def __init__(self, module_path: Path) -> None:
        """Initialise extractor for a module.

        Args:
            module_path: Path to the module package (directory containing
                `__init__.py`).
        """
        self.module_path = module_path
        self.init_file = module_path / "__init__.py"

    def extract(self) -> PublicApi:
        """Extract public API from the module's `__init__.py`.

        Returns:
            PublicApi describing all exported symbols and their categories.

        Raises:
            FileNotFoundError: If `__init__.py` does not exist.
            SyntaxError: If `__init__.py` cannot be parsed.
        """
        from abcdef.modularity.validation import PublicApi, PublicApiSymbol

        if not self.init_file.exists():
            return PublicApi.empty()

        source = self.init_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(self.init_file))

        exported_names = self._get_exported_names(tree)

        try:
            module = self._import_module()
        except Exception:
            return PublicApi(
                symbols=frozenset(
                    PublicApiSymbol(name=n, kind="unknown", full_path=n)
                    for n in exported_names
                ),
                commands=frozenset(),
                queries=frozenset(),
                events=frozenset(),
                spis=frozenset(),
            )

        return self._categorise(module, exported_names)

    def _categorise(self, module: ModuleType, exported_names: set[str]) -> PublicApi:
        """Categorise exported symbols by inspecting runtime markers.

        Args:
            module: Imported module object.
            exported_names: Names to inspect.

        Returns:
            PublicApi with symbols sorted into categories.
        """
        from abcdef.modularity.validation import PublicApi, PublicApiSymbol

        symbols: list[PublicApiSymbol] = []
        commands: list[PublicApiSymbol] = []
        queries: list[PublicApiSymbol] = []
        events: list[PublicApiSymbol] = []
        spis: list[PublicApiSymbol] = []

        for name in exported_names:
            obj = getattr(module, name, None)
            if obj is None or not isinstance(obj, type):
                continue

            full_path = f"{module.__name__}.{name}"
            symbol = PublicApiSymbol(name=name, kind="unknown", full_path=full_path)
            symbols.append(symbol)

            cqrs_marker = _get_marker(obj, "__cqrs_type__")
            ddd_marker = _get_marker(obj, "__ddd_type__")
            modularity_marker = _get_marker(obj, "__modularity_type__")

            if cqrs_marker == "command":
                symbol = PublicApiSymbol(name=name, kind="command", full_path=full_path)
                commands.append(symbol)
                symbols[-1] = symbol
            elif cqrs_marker == "query":
                symbol = PublicApiSymbol(name=name, kind="query", full_path=full_path)
                queries.append(symbol)
                symbols[-1] = symbol
            elif ddd_marker == "domain_event":
                symbol = PublicApiSymbol(name=name, kind="event", full_path=full_path)
                events.append(symbol)
                symbols[-1] = symbol
            elif modularity_marker == "spi":
                symbol = PublicApiSymbol(name=name, kind="spi", full_path=full_path)
                spis.append(symbol)
                symbols[-1] = symbol

        return PublicApi(
            symbols=frozenset(symbols),
            commands=frozenset(commands),
            queries=frozenset(queries),
            events=frozenset(events),
            spis=frozenset(spis),
        )

    def _get_exported_names(self, tree: ast.Module) -> set[str]:
        """Discover exported symbol names from AST.

        If `__all__` is defined, use that. Otherwise, infer from top-level
        assignments and imports that are not marked as private.

        Args:
            tree: The parsed AST of `__init__.py`.

        Returns:
            Set of exported symbol names.
        """
        names = self._names_from_all(tree)
        if names is not None:
            return names
        return self._infer_exported_names(tree)

    @staticmethod
    def _names_from_all(tree: ast.Module) -> set[str] | None:
        """Extract names from ``__all__`` if present.

        Args:
            tree: Parsed AST of ``__init__.py``.

        Returns:
            Set of names from ``__all__``, or None if not defined.
        """
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, ast.List)
                    ):
                        return {
                            str(elt.value)
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        }
        return None

    @staticmethod
    def _infer_exported_names(tree: ast.Module) -> set[str]:
        """Infer exported names from top-level imports and assignments.

        Args:
            tree: Parsed AST of ``__init__.py``.

        Returns:
            Set of inferred public names (excluding private ``_`` prefixed names).
        """
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                names.update(_names_from_import_from(node))
            elif isinstance(node, ast.Import):
                names.update(_names_from_import(node))
            elif isinstance(node, ast.Assign):
                names.update(_names_from_assign(node))
        return names

    def _import_module(self) -> ModuleType:
        """Import the module for runtime marker inspection.

        Returns:
            The imported module object.

        Raises:
            ImportError: If the module cannot be imported.
        """
        rel_path = self.module_path.relative_to(self.module_path.parent.parent)
        module_name = ".".join(rel_path.parts)

        if module_name in sys.modules:
            return sys.modules[module_name]

        try:
            __import__(module_name)
            return sys.modules[module_name]
        except ImportError as e:
            raise ImportError(
                f"Cannot import module '{module_name}' for marker inspection"
            ) from e


def _names_from_import_from(node: ast.ImportFrom) -> set[str]:
    """Collect public names from a ``from x import y`` node.

    Args:
        node: AST ImportFrom node.

    Returns:
        Public names (no ``_`` prefix).
    """
    names: set[str] = set()
    for alias in node.names:
        imported_name = alias.asname or alias.name
        if not imported_name.startswith("_"):
            names.add(imported_name)
    return names


def _names_from_import(node: ast.Import) -> set[str]:
    """Collect public names from an ``import x`` node.

    Args:
        node: AST Import node.

    Returns:
        Public top-level names (no ``_`` prefix).
    """
    names: set[str] = set()
    for alias in node.names:
        imported_name = alias.asname or alias.name
        if not imported_name.startswith("_"):
            names.add(imported_name.split(".")[0])
    return names


def _names_from_assign(node: ast.Assign) -> set[str]:
    """Collect public names from a top-level assignment node.

    Args:
        node: AST Assign node.

    Returns:
        Public names (no ``_`` prefix).
    """
    names: set[str] = set()
    for target in node.targets:
        if isinstance(target, ast.Name) and not target.id.startswith("_"):
            names.add(target.id)
    return names
