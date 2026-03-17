"""Enforce import boundary rules for `abcdef` packages.

Each package may only import from the packages listed in the allowed
matrix. Any import that crosses a forbidden boundary causes a test
failure naming the offending file and the disallowed import.

Allowed import matrix
---------------------
- `b/`: b/ only
- `c/`: b/ only
- `d/`: b/ only
- `de/`: b/, `d/`

Package facade rule
-------------------
Each package `__init__.py` may only re-export symbols from its own
namespace.

Rules
-----
- Intra-package imports (a file importing from its own package) are
  always allowed and are not checked.
- Imports guarded by ``if TYPE_CHECKING`` are excluded. They carry no
  runtime dependency and are not subject to boundary checks.
- Runtime boundary checks exclude ``__init__.py`` files.
- Package facade checks inspect ``__init__.py`` files separately.
"""

from __future__ import annotations

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ABCDEF = Path(__file__).parents[2] / "src" / "abcdef"
_B = _ABCDEF / "b"
_C = _ABCDEF / "c"
_D = _ABCDEF / "d"
_DE = _ABCDEF / "de"
_IN_MEMORY = _ABCDEF / "in_memory"
_SPECIFICATION = _ABCDEF / "specification"
_MODULARITY = _ABCDEF / "modularity"

# ---------------------------------------------------------------------------
# Allowed import prefixes per sub-package
#
# Each entry maps a source directory to the set of abcdef-internal
# import prefixes that files inside it may import FROM OTHER PACKAGES.
# Intra-package imports are always allowed and handled separately.
# ---------------------------------------------------------------------------

_B_PREFIXES = {"abcdef.b"}

_ALLOWED: dict[Path, set[str]] = {
    _B: _B_PREFIXES,
    _C: _B_PREFIXES,
    _D: _B_PREFIXES,
    _DE: _B_PREFIXES | {"abcdef.d"},
    _MODULARITY: _B_PREFIXES,
}

_PACKAGE_FACADES = {
    _B,
    _C,
    _D,
    _DE,
    _IN_MEMORY,
    _SPECIFICATION,
    _MODULARITY,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _guarded_import_ids(tree: ast.Module) -> set[int]:
    """Return ids of import nodes inside TYPE_CHECKING blocks.

    Collects the object ids of every ``ast.Import`` and
    ``ast.ImportFrom`` node that appears inside a top-level
    ``if TYPE_CHECKING:`` guard. These carry no runtime dependency
    and are excluded from boundary checks.

    Args:
        tree: Parsed AST of a source file.

    Returns:
        Set of ``id()`` values of guarded import nodes.
    """
    guarded: set[int] = set()
    for node in ast.iter_child_nodes(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_type_checking = (
            isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"
        ) or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
        if not is_type_checking:
            continue
        for child in ast.walk(node):
            if isinstance(child, (ast.Import, ast.ImportFrom)):
                guarded.add(id(child))
    return guarded


def _abcdef_imports(path: Path) -> list[str]:
    """Return runtime abcdef-internal imports found in a source file.

    Handles both ``import x.y`` and ``from x.y import z`` forms,
    converting relative imports to absolute using the file's package.
    Imports inside ``TYPE_CHECKING`` blocks are excluded.

    Args:
        path: Path to a Python source file.

    Returns:
        List of absolute module strings that start with ``abcdef``.
    """
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    guarded = _guarded_import_ids(tree)

    # Derive the absolute package prefix for relative imports.
    # e.g. abcdef/c/command.py -> ('abcdef', 'c')
    rel = path.relative_to(_ABCDEF.parent)
    parts = rel.with_suffix("").parts
    package_parts = parts[:-1]

    results: list[str] = []
    for node in ast.walk(tree):
        if id(node) in guarded:
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("abcdef"):
                    results.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module and node.module.startswith("abcdef"):
                    results.append(node.module)
            else:
                base = package_parts[: len(package_parts) - (node.level - 1)]
                module_suffix = node.module or ""
                absolute = ".".join(base) + (
                    f".{module_suffix}" if module_suffix else ""
                )
                if absolute.startswith("abcdef"):
                    results.append(absolute)
    return results


def _own_prefix(directory: Path) -> str:
    """Return the abcdef import prefix for a directory.

    Args:
        directory: A sub-package directory under abcdef/.

    Returns:
        Dotted module prefix, e.g. ``abcdef.c``.
    """
    rel = directory.relative_to(_ABCDEF.parent)
    return ".".join(rel.parts)


def _is_allowed(import_str: str, allowed: set[str], own: str) -> bool:
    """Return True if import_str is permitted.

    Intra-package imports (starting with the file's own prefix) are
    always allowed. External imports must match an allowed prefix.

    Args:
        import_str: Absolute module string, e.g. ``abcdef.c.markers``.
        allowed: Set of permitted external module prefixes.
        own: The file's own package prefix (always permitted).

    Returns:
        True if the import is allowed.
    """
    if import_str == own or import_str.startswith(own + "."):
        return True
    return any(
        import_str == prefix or import_str.startswith(prefix + ".")
        for prefix in allowed
    )


def _violations(
    directory: Path,
    allowed: set[str],
) -> list[str]:
    """Collect boundary violations for .py files in a directory.

    Skips ``__init__.py`` in all cases.

    Args:
        directory: The sub-package directory to check.
        allowed: Permitted external abcdef import prefixes.

    Returns:
        List of human-readable violation strings.
    """
    own = _own_prefix(directory)
    found: list[str] = []
    for py_file in sorted(directory.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        for imp in _abcdef_imports(py_file):
            if not _is_allowed(imp, allowed, own):
                rel = py_file.relative_to(_ABCDEF.parent)
                found.append(f"{rel}: forbidden import '{imp}'")
    return found


def _facade_violations(directory: Path) -> list[str]:
    """Collect facade re-export violations for a package `__init__.py`.

    A package facade may only re-export symbols from modules within its
    own namespace.

    Args:
        directory: Package directory containing `__init__.py`.

    Returns:
        List of human-readable violation strings.
    """
    init_file = directory / "__init__.py"
    own = _own_prefix(directory)
    found: list[str] = []
    for imp in _abcdef_imports(init_file):
        if imp != own and not imp.startswith(own + "."):
            rel = init_file.relative_to(_ABCDEF.parent)
            found.append(f"{rel}: foreign re-export import '{imp}'")
    return found


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestImportBoundaries:
    """Enforce the sub-package import boundary rules."""

    def test_b_imports_only_b(self) -> None:
        """b/ must only import from b/."""
        violations = _violations(_B, allowed=_ALLOWED[_B])
        assert violations == [], "\n" + "\n".join(violations)

    def test_c_imports_only_b(self) -> None:
        """c/ must only import from b/."""
        violations = _violations(_C, allowed=_ALLOWED[_C])
        assert violations == [], "\n" + "\n".join(violations)

    def test_d_imports_only_b(self) -> None:
        """d/ must only import from b/."""
        violations = _violations(_D, allowed=_ALLOWED[_D])
        assert violations == [], "\n" + "\n".join(violations)

    def test_de_imports_only_b_and_d(self) -> None:
        """de/ must only import from b/ and d/."""
        violations = _violations(_DE, allowed=_ALLOWED[_DE])
        assert violations == [], "\n" + "\n".join(violations)

    def test_package_facades_only_re_export_own_namespace(self) -> None:
        """Each package facade must only re-export its own namespace."""
        violations: list[str] = []
        for directory in sorted(_PACKAGE_FACADES):
            violations.extend(_facade_violations(directory))

        assert violations == [], "\n" + "\n".join(violations)
