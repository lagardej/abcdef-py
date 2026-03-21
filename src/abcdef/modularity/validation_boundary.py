"""Boundary validation for modularity modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from abcdef.modularity.module import Module
    from abcdef.modularity.validation import Violation


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

        return violations
