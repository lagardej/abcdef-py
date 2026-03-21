"""Boundary validation for modularity modules."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from abcdef.modularity.validation import Violation

if TYPE_CHECKING:
    from collections.abc import Sequence

    from abcdef.modularity.module import Module


class BoundaryValidator:
    """Validates modularity architectural constraints."""

    def __init__(self, modules: Sequence[Module]) -> None:
        """Initialise validator with modules.

        Args:
            modules: All discovered modules to validate.
        """
        self.modules = modules
        self._module_by_name = {m.declaration.name: m for m in modules}

    def validate(self) -> list[Violation]:
        """Run all validation checks.

        Returns:
            List of violations found (empty if valid).
        """
        violations: list[Violation] = []
        violations += self._check_facade_rule()
        violations += self._check_import_boundary()
        return violations

    def _check_facade_rule(self) -> list[Violation]:
        """Check that module roots do not import from .internal subpackages."""
        violations: list[Violation] = []
        for m in self.modules:
            init_file = m.path / "__init__.py"
            if not init_file.exists():
                continue
            try:
                source = init_file.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(init_file))
            except Exception:
                continue

            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if node.level != 1 or not node.module:
                    continue
                parts = node.module.split(".")
                if parts and parts[0] == "internal":
                    msg = f"Module root imports from internal: {node.module}"
                    violations.append(
                        Violation(
                            module_name=m.declaration.name,
                            violation_type="facade_rule",
                            message=msg,
                            location=str(init_file),
                        )
                    )
                    break  # One per module
        return violations

    def _check_import_boundary(self) -> list[Violation]:
        """Check that no module imports from another module's internal subpackage."""
        violations: list[Violation] = []
        # Set of forbidden internal prefixes for all modules
        forbidden = {f"{name}.internal" for name in self._module_by_name}

        for m in self.modules:
            for py_file in m.path.rglob("*.py"):
                try:
                    source = py_file.read_text(encoding="utf-8")
                    tree = ast.parse(source, filename=str(py_file))
                except Exception:
                    continue

                for node in ast.walk(tree):
                    if not isinstance(node, ast.ImportFrom):
                        continue
                    if node.level != 0 or not node.module:
                        continue
                    # Allow self-internal imports
                    self_prefix = f"{m.declaration.name}.internal"
                    if node.module.startswith(self_prefix):
                        continue
                    # Check against all forbidden prefixes
                    for prefix in forbidden:
                        if node.module == prefix or node.module.startswith(
                            prefix + "."
                        ):
                            msg = f"Imports from {prefix}: {node.module}"
                            violations.append(
                                Violation(
                                    module_name=m.declaration.name,
                                    violation_type="import_boundary",
                                    message=msg,
                                    location=str(py_file),
                                )
                            )
                            break  # One per file
        return violations
