"""Public API extraction from module root exports.

Uses AST analysis to discover exported symbols and marker inspection to
categorise them.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import TYPE_CHECKING, cast

from abcdef.modulith.validation import PublicApi, PublicApiSymbol

if TYPE_CHECKING:
    from types import ModuleType


def _get_marker(cls: type, marker_attr: str) -> str | None:
    """Get marker value from class or its parents.

    Args:
        cls: The class to inspect.
        marker_attr: The marker attribute name (``__cqrs_type__``, ``__ddd_type__``,
            ``__de_type__``, ``__modulith_type__``, or ``__specification_type__``).

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
        if not self.init_file.exists():
            return PublicApi.empty()

        source = self.init_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(self.init_file))

        # Collect all exported names from __all__ or infer from imports/assignments
        exported_names = self._get_exported_names(tree)

        # Try to import the module to inspect marker values
        try:
            module = self._import_module()
        except Exception:
            # If import fails, return symbols without categorisation
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

        # Categorise each exported symbol by inspecting markers
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

            # Check markers in priority order
            cqrs_marker = _get_marker(obj, "__cqrs_type__")
            ddd_marker = _get_marker(obj, "__ddd_type__")
            modulith_marker = _get_marker(obj, "__modulith_type__")

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
            elif modulith_marker == "spi":
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
        # Check for __all__
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            names = set()
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    names.add(str(elt.value))
                            return names

        # Fallback: infer from top-level imports and assignments (not private)
        names = set()
        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imported_name = alias.asname or alias.name
                    if not imported_name.startswith("_"):
                        names.add(imported_name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imported_name = alias.asname or alias.name
                    if not imported_name.startswith("_"):
                        names.add(imported_name.split(".")[0])
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and not target.id.startswith("_"):
                        names.add(target.id)

        return names

    def _import_module(self) -> ModuleType:
        """Import the module for runtime marker inspection.

        Returns:
            The imported module object.

        Raises:
            ImportError: If the module cannot be imported.
        """
        # Derive module name from path
        rel_path = self.module_path.relative_to(self.module_path.parent.parent)
        module_name = ".".join(rel_path.parts)

        if module_name in sys.modules:
            return sys.modules[module_name]

        # Try to import
        try:
            __import__(module_name)
            return sys.modules[module_name]
        except ImportError as e:
            raise ImportError(
                f"Cannot import module '{module_name}' for marker inspection"
            ) from e
