"""ABCDEF Modularity — Modular architecture validation and documentation.

Provides tools for application developers to declare, validate, and document
the modular structure of their applications.

Public API:

    Modularity              -- entry point: discover(), validate(), generate_docs()
    CommandModule, QueryModule  -- module types
    Violation             -- validation error
    PublicApi             -- discovered module public API

Markers for module declaration (use in __init__.py):

    __modularity__          -- dict with 'type' (and optional 'name', 'description')
    @spi                  -- marks abstract classes exposed as contracts (optional)

Examples:
    >>> from pathlib import Path
    >>> from abcdef.modularity import Modularity
    >>>
    >>> modularity = Modularity(Path.cwd())
    >>> modules = modularity.discover()
    >>> violations = modularity.validate()
    >>> docs = modularity.generate_docs()
"""

from abcdef.modularity.extraction import PublicApiExtractor
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE, SPI
from abcdef.modularity.modularity import Modularity
from abcdef.modularity.module import (
    CommandModule,
    Module,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modularity.report import MarkdownReporter
from abcdef.modularity.validation import PublicApi, PublicApiSymbol, Violation
from abcdef.modularity.validation_boundary import BoundaryValidator

__all__ = [
    "COMMAND_MODULE",
    "QUERY_MODULE",
    "SPI",
    "BoundaryValidator",
    "CommandModule",
    "MarkdownReporter",
    "Modularity",
    "Module",
    "ModuleDeclaration",
    "PublicApi",
    "PublicApiExtractor",
    "PublicApiSymbol",
    "QueryModule",
    "Violation",
]
