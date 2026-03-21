"""Modularity — modularity discovery, validation, and documentation generation."""

from __future__ import annotations

import ast
from typing import TYPE_CHECKING

from abcdef.modularity.extraction import PublicApiExtractor
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.module import (
    CommandModule,
    Module,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modularity.report import MarkdownReporter
from abcdef.modularity.validation_boundary import BoundaryValidator

if TYPE_CHECKING:
    from pathlib import Path

    from abcdef.modularity.validation import PublicApi, Violation


class Modularity:
    """Discover, validate, and document modules in an application.

    Scans a project for packages declaring `__modularity__` metadata and
    enforces architectural constraints.
    """

    def __init__(self, root_path: Path) -> None:
        """Initialise modularity for a project.

        Args:
            root_path: Root directory of the project (the package parent).
                For example, if modules are at `myapp/orders/`, pass the
                directory containing `myapp/`.
        """
        self.root_path = root_path
        self.modules: list[Module] = []

    def discover(self) -> list[Module]:
        """Discover all declared modules.

        Scans the project for packages with `__modularity__` declaration in
        `__init__.py` and loads them as Module objects.

        Returns:
            List of discovered modules (also stored in self.modules).

        Raises:
            ValueError: If a module declaration is invalid.
        """
        from abcdef.modularity.validation import PublicApi

        self.modules = []

        for path in self.root_path.iterdir():
            if not path.is_dir():
                continue

            init_file = path / "__init__.py"
            if not init_file.exists():
                continue

            try:
                decl = self._read_declaration(init_file, path)
            except ValueError:
                # Invalid declaration, skip this package
                continue

            if decl is None:
                # No __modularity__ declaration, skip
                continue

            try:
                extractor = PublicApiExtractor(path)
                api = extractor.extract()
            except Exception:
                # If API extraction fails, use empty API
                api = PublicApi.empty()

            module = self._create_module(decl, path, api)
            self.modules.append(module)

        return self.modules

    def validate(self) -> list[Violation]:
        """Validate all discovered modules.

        Checks:
        - Read/write constraints (command vs query)
        - Facade rule (root exports only)
        - Import boundaries (layers only import from module roots)

        Returns:
            List of violations (empty if valid).
        """
        validator = BoundaryValidator(self.modules)
        return validator.validate()

    def generate_docs(self) -> str:
        """Generate Markdown documentation for all modules.

        Returns:
            Markdown string describing modules, their public APIs, and
            inter-module communication.
        """
        reporter = MarkdownReporter(self.modules)
        return reporter.generate()

    @staticmethod
    def _read_declaration(
        init_file: Path, module_path: Path
    ) -> ModuleDeclaration | None:
        """Read module declaration from __init__.py.

        Looks for `__modularity__` dict with `type` and optional `name`.
        Extracts module docstring as description if not set.

        Args:
            init_file: Path to __init__.py.
            module_path: Path to module directory.

        Returns:
            ModuleDeclaration if found, None otherwise.

        Raises:
            ValueError: If declaration is invalid.
        """
        source = init_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(init_file))

        modularity_dict = Modularity._extract_modularity_dict(tree)
        if modularity_dict is None:
            return None

        return Modularity._build_declaration(
            init_file, module_path, tree, modularity_dict
        )

    @staticmethod
    def _extract_modularity_dict(tree: ast.Module) -> dict[str, str] | None:
        """Extract the ``__modularity__`` dict literal from AST.

        Args:
            tree: Parsed AST of ``__init__.py``.

        Returns:
            Dict of string key/value pairs if found, None otherwise.
        """
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.Assign):
                continue
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__modularity__"
                    and isinstance(node.value, ast.Dict)
                ):
                    result: dict[str, str] = {}
                    for key, value in zip(
                        node.value.keys, node.value.values, strict=False
                    ):
                        if (
                            isinstance(key, ast.Constant)
                            and isinstance(value, ast.Constant)
                            and isinstance(key.value, str)
                            and isinstance(value.value, str)
                        ):
                            result[key.value] = value.value
                    return result
        return None

    @staticmethod
    def _build_declaration(
        init_file: Path,
        module_path: Path,
        tree: ast.Module,
        modularity_dict: dict[str, str],
    ) -> ModuleDeclaration:
        """Build a ModuleDeclaration from a parsed modularity dict.

        Args:
            init_file: Path to __init__.py (for error messages).
            module_path: Path to module directory.
            tree: Parsed AST (for docstring extraction).
            modularity_dict: Extracted ``__modularity__`` key/value pairs.

        Returns:
            Populated ModuleDeclaration.

        Raises:
            ValueError: If the declaration is missing required fields or has invalid
                values.
        """
        module_type = modularity_dict.get("type")
        if not module_type:
            raise ValueError(
                f"{init_file}: __modularity__ declaration missing required 'type'"
            )

        if module_type not in (COMMAND_MODULE, QUERY_MODULE):
            raise ValueError(
                f"{init_file}: __modularity__['type'] must be "
                f"'{COMMAND_MODULE}' or '{QUERY_MODULE}', got '{module_type}'"
            )

        name = modularity_dict.get("name") or module_path.name
        module_docstring = ast.get_docstring(tree)
        description = modularity_dict.get("description") or (module_docstring or "")

        return ModuleDeclaration(
            module_type=module_type, name=name, description=description
        )

    @staticmethod
    def _create_module(
        decl: ModuleDeclaration, module_path: Path, api: PublicApi
    ) -> Module:
        """Create a Module instance from declaration and API.

        Args:
            decl: Module declaration.
            module_path: Filesystem path.
            api: Extracted public API.

        Returns:
            CommandModule or QueryModule instance.
        """
        if decl.module_type == COMMAND_MODULE:
            return CommandModule(_declaration=decl, _path=module_path, _public_api=api)
        elif decl.module_type == QUERY_MODULE:
            return QueryModule(_declaration=decl, _path=module_path, _public_api=api)
        else:
            raise ValueError(f"Unknown module type: {decl.module_type}")
