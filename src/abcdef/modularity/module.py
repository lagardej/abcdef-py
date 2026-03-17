"""Module definition and types."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE

if TYPE_CHECKING:
    from pathlib import Path

    from abcdef.modularity.validation import PublicApi


@dataclass(frozen=True)
class ModuleDeclaration:
    """Module metadata declared in __init__.py.

    Attributes:
        module_type: Either "command_module" or "query_module".
        name: Logical name of the module (for documentation).
        description: Human-readable description (from docstring or explicit).
    """

    module_type: str
    name: str
    description: str = ""


class Module(ABC):
    """Abstract base class for a declared module."""

    @property
    @abstractmethod
    def declaration(self) -> ModuleDeclaration:
        """Module declaration metadata."""
        ...

    @property
    @abstractmethod
    def path(self) -> Path:
        """Filesystem path to the module package."""
        ...

    @property
    @abstractmethod
    def public_api(self) -> PublicApi:
        """Discovered public API."""
        ...


@dataclass(frozen=True)
class CommandModule(Module):
    """A command module (write side).

    Maintains aggregates, enforces invariants, publishes domain events.

    Attributes:
        _declaration: Module metadata.
        _path: Filesystem path to module.
        _public_api: Extracted public API.
    """

    _declaration: ModuleDeclaration
    _path: Path
    _public_api: PublicApi

    @property
    def declaration(self) -> ModuleDeclaration:
        """Module declaration metadata."""
        return self._declaration

    @property
    def path(self) -> Path:
        """Filesystem path to the module package."""
        return self._path

    @property
    def public_api(self) -> PublicApi:
        """Discovered public API."""
        return self._public_api

    def __post_init__(self) -> None:
        """Validate declaration."""
        if self._declaration.module_type != COMMAND_MODULE:
            raise ValueError(
                f"CommandModule requires module_type={COMMAND_MODULE!r}, "
                f"got {self._declaration.module_type!r}"
            )


@dataclass(frozen=True)
class QueryModule(Module):
    """A query module (read side).

    Projects events into read models, serves queries without state mutation.

    Attributes:
        _declaration: Module metadata.
        _path: Filesystem path to module.
        _public_api: Extracted public API.
    """

    _declaration: ModuleDeclaration
    _path: Path
    _public_api: PublicApi

    @property
    def declaration(self) -> ModuleDeclaration:
        """Module declaration metadata."""
        return self._declaration

    @property
    def path(self) -> Path:
        """Filesystem path to the module package."""
        return self._path

    @property
    def public_api(self) -> PublicApi:
        """Discovered public API."""
        return self._public_api

    def __post_init__(self) -> None:
        """Validate declaration."""
        if self._declaration.module_type != QUERY_MODULE:
            raise ValueError(
                f"QueryModule requires module_type={QUERY_MODULE!r}, "
                f"got {self._declaration.module_type!r}"
            )
