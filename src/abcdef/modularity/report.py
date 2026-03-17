"""Documentation generation from modularity metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abcdef.modularity.module import Module


class MarkdownReporter:
    """Generates Markdown documentation from module metadata.

    Focuses on module public API and inter-module communication (events, SPIs).
    Omits internal implementation details.
    """

    def __init__(self, modules: list[Module]) -> None:
        """Initialise reporter with modules.

        Args:
            modules: All modules to document.
        """
        self.modules = sorted(modules, key=lambda m: m.declaration.name)

    def generate(self) -> str:
        """Generate complete module documentation.

        Returns:
            Markdown documentation covering all modules.
        """
        lines: list[str] = []

        lines.append("# Module Documentation")
        lines.append("")
        lines.append(
            "This document describes the public API and inter-module communication"
        )
        lines.append(
            "for all modules in the application. Implementation details are omitted."
        )
        lines.append("")

        # Table of contents
        lines.append("## Modules")
        lines.append("")
        for module in self.modules:
            decl = module.declaration
            lines.append(f"- [{decl.name}](#{decl.name})")
        lines.append("")

        # Per-module sections
        for module in self.modules:
            lines.extend(self._module_section(module))
            lines.append("")

        return "\n".join(lines)

    def _module_section(self, module: Module) -> list[str]:
        """Generate documentation for a single module.

        Args:
            module: Module to document.

        Returns:
            List of markdown lines.
        """
        lines: list[str] = []
        decl = module.declaration
        api = module.public_api

        # Header
        lines.append(f"### {decl.name}")
        lines.append("")

        # Type and description
        lines.append(f"**Type:** {decl.module_type.replace('_', ' ').title()}")
        lines.append("")

        if decl.description:
            lines.append(decl.description)
            lines.append("")

        # Public API
        if api.symbols:
            lines.append("#### Public API")
            lines.append("")

            # Commands
            if api.commands:
                lines.append("**Commands:**")
                lines.append("")
                for symbol in sorted(api.commands, key=lambda s: s.name):
                    lines.append(f"- `{symbol.name}` — {symbol.full_path}")
                lines.append("")

            # Queries
            if api.queries:
                lines.append("**Queries:**")
                lines.append("")
                for symbol in sorted(api.queries, key=lambda s: s.name):
                    lines.append(f"- `{symbol.name}` — {symbol.full_path}")
                lines.append("")

            # Events published
            if api.events:
                lines.append("**Events Published:**")
                lines.append("")
                for symbol in sorted(api.events, key=lambda s: s.name):
                    lines.append(f"- `{symbol.name}` — {symbol.full_path}")
                lines.append("")

            # SPIs
            if api.spis:
                lines.append("**Service Provider Interfaces (SPIs):**")
                lines.append("")
                for symbol in sorted(api.spis, key=lambda s: s.name):
                    lines.append(f"- `{symbol.name}` — {symbol.full_path}")
                lines.append("")

        return lines
