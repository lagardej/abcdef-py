"""Documentation generation from modularity metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from abcdef.modularity.module import Module
    from abcdef.modularity.validation import PublicApi, PublicApiSymbol


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

        lines.append(f"### {decl.name}")
        lines.append("")
        lines.append(f"**Type:** {decl.module_type.replace('_', ' ').title()}")
        lines.append("")

        if decl.description:
            lines.append(decl.description)
            lines.append("")

        if api.symbols:
            lines.append("#### Public API")
            lines.append("")
            lines.extend(self._api_section(api))

        return lines

    @staticmethod
    def _api_section(api: PublicApi) -> list[str]:
        """Render the public API subsection for a module.

        Args:
            api: Extracted public API.

        Returns:
            List of markdown lines.
        """
        lines: list[str] = []

        if api.commands:
            lines.extend(_symbol_block("Commands", api.commands))
        if api.queries:
            lines.extend(_symbol_block("Queries", api.queries))
        if api.events:
            lines.extend(_symbol_block("Events Published", api.events))
        if api.spis:
            lines.extend(_symbol_block("Service Provider Interfaces (SPIs)", api.spis))

        return lines


def _symbol_block(heading: str, symbols: frozenset[PublicApiSymbol]) -> list[str]:
    """Render a labelled block of symbols.

    Args:
        heading: Section heading (e.g. ``"Commands"``).
        symbols: Symbols to list.

    Returns:
        List of markdown lines.
    """
    lines: list[str] = []
    lines.append(f"**{heading}:**")
    lines.append("")
    for symbol in sorted(symbols, key=lambda s: s.name):
        lines.append(f"- `{symbol.name}` — {symbol.full_path}")
    lines.append("")
    return lines
