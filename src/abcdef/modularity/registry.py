"""Modularity — modularity discovery, validation, and documentation generation."""

from __future__ import annotations

import ast
from pathlib import Path

from abcdef.modularity.extraction import PublicApiExtractor
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.module import (
    CommandModule,
    Module,
    ModuleDeclaration,
    QueryModule,
)
from abcdef.modularity.report import MarkdownReporter
from abcdef.modularity.validation import Violation
from abcdef.modularity.validation_boundary import BoundaryValidator


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
        self.modules = []

        # Find all packages with __modularity__ declaration
        for init_file in self.root_path.rglob("__init__.py"):
            module_path = init_file.parent

            # Skip abcdef itself
            if "abcdef" in module_path.parts:
                continue

            # Skip tests and build directories
            if any(p in module_path.parts for p in ("tests", ".venv", "venv", "build")):
                continue

            decl = self._read_declaration(init_file, module_path)
            if decl is None:
                continue

            api_extractor = PublicApiExtractor(module_path)
            api = api_extractor.extract()

            module = self._create_module(decl, module_path, api)
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

        # Extract __modularity__ dict and module docstring
        modularity_dict: dict[str, str] | None = None
        module_docstring = ast.get_docstring(tree)

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__modularity__":
                        if isinstance(node.value, ast.Dict):
                            modularity_dict = {}
                            for key, value in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Constant) and isinstance(
                                    value, ast.Constant
                                ):
                                    modularity_dict[key.value] = value.value

        if modularity_dict is None:
            return None

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

        # Logical name: explicit or inferred from package name
        name = modularity_dict.get("name") or module_path.name

        # Description: explicit or from docstring
        description = modularity_dict.get("description") or (module_docstring or "")

        return ModuleDeclaration(
            module_type=module_type, name=name, description=description
        )

    @staticmethod
    def _create_module(decl: ModuleDeclaration, module_path: Path, api) -> Module:
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
