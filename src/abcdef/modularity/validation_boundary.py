"""Boundary validation for modularity modules."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.validation import Violation

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

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

        for module in self.modules:
            violations.extend(self._validate_read_write_constraints(module))
            violations.extend(self._validate_facade_rule(module))
            violations.extend(self._validate_import_boundaries(module))

        return violations

    def _validate_read_write_constraints(self, module: Module) -> list[Violation]:
        """Validate command vs query module constraints.

        Command modules must not export queries.
        Query modules must not export commands.

        Args:
            module: Module to validate.

        Returns:
            Violations found.
        """
        violations: list[Violation] = []
        api = module.public_api
        decl = module.declaration

        if decl.module_type == COMMAND_MODULE:
            if api.queries:
                query_names = ", ".join(s.name for s in api.queries)
                violations.append(
                    Violation(
                        module_name=decl.name,
                        violation_type="read_write_constraint",
                        message=(
                            f"Command module exports queries: {query_names}. "
                            "Command modules must only export commands and events."
                        ),
                        location=str(module.path / "__init__.py"),
                    )
                )

        elif decl.module_type == QUERY_MODULE and api.commands:
            command_names = ", ".join(s.name for s in api.commands)
            violations.append(
                Violation(
                    module_name=decl.name,
                    violation_type="read_write_constraint",
                    message=(
                        f"Query module exports commands: {command_names}. "
                        "Query modules must only export queries and documents."
                    ),
                    location=str(module.path / "__init__.py"),
                )
            )

        return violations

    def _validate_facade_rule(self, module: Module) -> list[Violation]:
        """Validate that module facade only re-exports its own namespace.

        Args:
            module: Module to validate.

        Returns:
            Violations found.
        """
        violations: list[Violation] = []
        init_file = module.path / "__init__.py"

        if not init_file.exists():
            return violations

        source = init_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(init_file))

        module_prefix = self._module_name_from_path(module.path)

        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module and node.module.startswith("abcdef"):
                continue
            if node.module and not (
                node.module == module_prefix
                or node.module.startswith(module_prefix + ".")
            ):
                violations.append(
                    Violation(
                        module_name=module.declaration.name,
                        violation_type="facade_rule",
                        message=(
                            f"Facade re-exports from foreign module: {node.module}."
                            " Module __init__.py may only re-export from its own"
                            " namespace."
                        ),
                        location=str(init_file),
                    )
                )

        return violations

    def _validate_import_boundaries(self, module: Module) -> list[Violation]:
        """Validate import boundaries between modules.

        Modules must only import from other modules' root (public API).

        Args:
            module: Module to validate.

        Returns:
            Violations found.
        """
        violations: list[Violation] = []
        module_prefix = self._module_name_from_path(module.path)

        # Scan all .py files in layers
        # (domain, application, projection, infrastructure, endpoint)
        for py_file in module.path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            if py_file.parent == module.path:
                continue

            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))

            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if node.module and node.module.startswith("abcdef"):
                    continue

                if node.module:
                    other_module_name = self._extract_module_name(node.module)
                    if (
                        other_module_name in self._module_by_name
                        and other_module_name != module_prefix
                        and not self._is_root_import(node.module, other_module_name)
                    ):
                        rel_file = py_file.relative_to(module.path)
                        violations.append(
                            Violation(
                                module_name=module.declaration.name,
                                violation_type="import_boundary",
                                message=(
                                    "Layer imports from other module internals:"
                                    f" '{node.module}'."
                                    " Must import from module root only."
                                ),
                                location=f"{module.declaration.name}/{rel_file}",
                            )
                        )

        return violations

    @staticmethod
    def _module_name_from_path(path: Path) -> str:
        """Derive module name from filesystem path.

        Args:
            path: Module directory path.

        Returns:
            Fully qualified module name.
        """
        parts = []
        for part in path.parts:
            if part in ("src", "abcdef"):
                break
            parts.append(part)
        return ".".join(parts) if parts else path.name

    @staticmethod
    def _extract_module_name(import_path: str) -> str:
        """Extract logical module name from an import path.

        Args:
            import_path: Full import string (e.g., 'myapp.orders.application.handlers').

        Returns:
            Logical module name (first two components, e.g., 'myapp.orders').
        """
        parts = import_path.split(".")
        return ".".join(parts[:2]) if len(parts) >= 2 else parts[0]

    @staticmethod
    def _is_root_import(import_path: str, module_name: str) -> bool:
        """Check if import is from a module's root.

        Args:
            import_path: Full import string.
            module_name: Module's logical name.

        Returns:
            True if importing from the module root (no deeper layers).
        """
        parts = import_path.split(".")
        module_parts = module_name.split(".")
        return len(parts) == len(module_parts)
