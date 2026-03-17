"""ABCDEF Modulith — Modular architecture validation and documentation.

Provides tools for application developers to declare, validate, and document
the modular structure of their applications.

Public API:

    Modulith              -- entry point: discover(), validate(), generate_docs()
    CommandModule, QueryModule  -- module types
    Violation             -- validation error
    PublicApi             -- discovered module public API

Markers for module declaration (use in __init__.py):

    __modulith__          -- dict with 'type' (and optional 'name', 'description')
    @spi                  -- marks abstract classes exposed as contracts (optional)

Examples:
    >>> from pathlib import Path
    >>> from abcdef.modulith import Modulith
    >>>
    >>> modulith = Modulith(Path.cwd())
    >>> modules = modulith.discover()
    >>> violations = modulith.validate()
    >>> docs = modulith.generate_docs()
"""

from abcdef.modulith.extraction import PublicApiExtractor
from abcdef.modulith.markers import COMMAND_MODULE, QUERY_MODULE, SPI
from abcdef.modulith.module import (
    CommandModule,
    Module,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modulith.registry import Modulith
from abcdef.modulith.report import MarkdownReporter
from abcdef.modulith.validation import PublicApi, PublicApiSymbol, Violation
from abcdef.modulith.validation_boundary import BoundaryValidator

__all__ = [
    "COMMAND_MODULE",
    "QUERY_MODULE",
    "SPI",
    "BoundaryValidator",
    "CommandModule",
    "MarkdownReporter",
    "Module",
    "ModuleDeclaration",
    "Modulith",
    "PublicApi",
    "PublicApiExtractor",
    "PublicApiSymbol",
    "QueryModule",
    "Violation",
]
