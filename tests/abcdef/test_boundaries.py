"""Enforce sub-package import boundary rules for abcdef/core/.

Each sub-package may only import from the packages listed in the allowed
matrix. Any import that crosses a forbidden boundary will cause a test
failure, naming the offending file and the disallowed import.

Allowed import matrix
---------------------
core root (event, message, result, markers) : other core root modules only
c/   : core root only
d/   : core root only
de/  : core root, d/

Rules
-----
- Intra-package imports (a file importing from its own package) are
  always allowed and are not checked.
- Imports guarded by ``if TYPE_CHECKING`` are excluded. They carry no
  runtime dependency and are not subject to boundary checks.
- ``__init__.py`` files are excluded. They aggregate and re-export
  across sub-packages by design.
"""

from __future__ import annotations

import ast
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ABCDEF = Path(__file__).parents[2] / "abcdef"
_CORE = _ABCDEF / "core"

_ROOT = _CORE
_C = _CORE / "c"
_D = _CORE / "d"
_DE = _CORE / "de"

# The core root modules subject to boundary checks. core/__init__.py is
# excluded -- it is the public facade and imports from all sub-packages.
_ROOT_MODULES = {"event.py", "message.py", "result.py", "markers.py"}

# ---------------------------------------------------------------------------
# Allowed import prefixes per sub-package
#
# Each entry maps a source directory to the set of abcdef-internal
# import prefixes that files inside it may import FROM OTHER PACKAGES.
# Intra-package imports are always allowed and handled separately.
# ---------------------------------------------------------------------------

_CORE_ROOT_PREFIXES = {
    "abcdef.core.event",
    "abcdef.core.message",
    "abcdef.core.result",
    "abcdef.core.markers",
}

_ALLOWED: dict[Path, set[str]] = {
    _ROOT: _CORE_ROOT_PREFIXES,  # root modules may import each other
    _C: _CORE_ROOT_PREFIXES,
    _D: _CORE_ROOT_PREFIXES,
    _DE: _CORE_ROOT_PREFIXES | {"abcdef.core.d"},
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
    # e.g. abcdef/core/c/command.py -> ('abcdef', 'core', 'c')
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
        Dotted module prefix, e.g. ``abcdef.core.c``.
    """
    rel = directory.relative_to(_ABCDEF.parent)
    return ".".join(rel.parts)


def _is_allowed(import_str: str, allowed: set[str], own: str) -> bool:
    """Return True if import_str is permitted.

    Intra-package imports (starting with the file's own prefix) are
    always allowed. External imports must match an allowed prefix.

    Args:
        import_str: Absolute module string, e.g. ``abcdef.core.c.markers``.
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
    include: set[str] | None = None,
) -> list[str]:
    """Collect boundary violations for .py files in a directory.

    Skips ``__init__.py`` in all cases.

    Args:
        directory: The sub-package directory to check.
        allowed: Permitted external abcdef import prefixes.
        include: If provided, only check files whose names are in this
            set. If None, check all non-__init__ .py files.

    Returns:
        List of human-readable violation strings.
    """
    own = _own_prefix(directory)
    found: list[str] = []
    for py_file in sorted(directory.glob("*.py")):
        if py_file.name == "__init__.py":
            continue
        if include is not None and py_file.name not in include:
            continue
        for imp in _abcdef_imports(py_file):
            if not _is_allowed(imp, allowed, own):
                rel = py_file.relative_to(_ABCDEF.parent)
                found.append(f"{rel}: forbidden import '{imp}'")
    return found


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestImportBoundaries:
    """Enforce the sub-package import boundary rules."""

    def test_core_root_imports_nothing_outside_root(self) -> None:
        """Core root modules may only import other core root modules."""
        violations = _violations(_ROOT, allowed=_ALLOWED[_ROOT], include=_ROOT_MODULES)
        assert violations == [], "\n" + "\n".join(violations)

    def test_c_imports_only_core_root(self) -> None:
        """c/ must only import from core root modules."""
        violations = _violations(_C, allowed=_ALLOWED[_C])
        assert violations == [], "\n" + "\n".join(violations)

    def test_d_imports_only_core_root(self) -> None:
        """d/ must only import from core root modules."""
        violations = _violations(_D, allowed=_ALLOWED[_D])
        assert violations == [], "\n" + "\n".join(violations)

    def test_de_imports_only_core_root_and_d(self) -> None:
        """de/ must only import from core root and d/."""
        violations = _violations(_DE, allowed=_ALLOWED[_DE])
        assert violations == [], "\n" + "\n".join(violations)
