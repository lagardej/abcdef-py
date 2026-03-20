"""Code generation logic for abcdef module and feature scaffolding."""

from __future__ import annotations

import ast
from pathlib import Path
from string import Template

from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE
from abcdef.modularity.registry import Modularity

_TEMPLATES_DIR = Path(__file__).parent / "templates"

ENDPOINT_CLI = "cli"
ENDPOINT_WEB = "web"
ENDPOINT_API = "api"
VALID_ENDPOINTS = (ENDPOINT_CLI, ENDPOINT_WEB, ENDPOINT_API)

# Files that are always generated regardless of endpoint selection.
_COMMAND_MODULE_BASE_FILES: list[tuple[str, str]] = [
    ("command_module/__init__.py.tmpl", "__init__.py"),
    ("command_module/domain/aggregate.py.tmpl", "domain/${module_name}.py"),
    (
        "command_module/domain/aggregate_repository.py.tmpl",
        "domain/${module_name}_repository.py",
    ),
    ("command_module/application/use_case.py.tmpl", "application/placeholder.py"),
    (
        "command_module/infrastructure/placeholder.py.tmpl",
        "infrastructure/placeholder.py",
    ),
]

_QUERY_MODULE_BASE_FILES: list[tuple[str, str]] = [
    ("query_module/__init__.py.tmpl", "__init__.py"),
    ("query_module/projection/document.py.tmpl", "projection/${module_name}.py"),
    ("query_module/application/query.py.tmpl", "application/placeholder.py"),
    (
        "query_module/infrastructure/placeholder.py.tmpl",
        "infrastructure/placeholder.py",
    ),
]

# Endpoint stubs for module scaffolding — keyed by (module_type, endpoint).
_MODULE_ENDPOINT_FILES: dict[tuple[str, str], tuple[str, str]] = {
    (COMMAND_MODULE, ENDPOINT_CLI): (
        "command_module/endpoint/cli/use_case.py.tmpl",
        "endpoint/cli/placeholder.py",
    ),
    (COMMAND_MODULE, ENDPOINT_WEB): (
        "command_module/endpoint/web/use_case.py.tmpl",
        "endpoint/web/placeholder.py",
    ),
    (COMMAND_MODULE, ENDPOINT_API): (
        "command_module/endpoint/api/use_case.py.tmpl",
        "endpoint/api/placeholder.py",
    ),
    (QUERY_MODULE, ENDPOINT_CLI): (
        "query_module/endpoint/cli/query.py.tmpl",
        "endpoint/cli/placeholder.py",
    ),
    (QUERY_MODULE, ENDPOINT_WEB): (
        "query_module/endpoint/web/query.py.tmpl",
        "endpoint/web/placeholder.py",
    ),
    (QUERY_MODULE, ENDPOINT_API): (
        "query_module/endpoint/api/query.py.tmpl",
        "endpoint/api/placeholder.py",
    ),
}

# Endpoint stubs for feature generation — keyed by (module_type, endpoint).
_FEATURE_ENDPOINT_FILES: dict[tuple[str, str], tuple[str, str]] = {
    (COMMAND_MODULE, ENDPOINT_CLI): (
        "command_module/endpoint/cli/use_case.py.tmpl",
        "endpoint/cli/${use_case_name}.py",
    ),
    (COMMAND_MODULE, ENDPOINT_WEB): (
        "command_module/endpoint/web/use_case.py.tmpl",
        "endpoint/web/${use_case_name}.py",
    ),
    (COMMAND_MODULE, ENDPOINT_API): (
        "command_module/endpoint/api/use_case.py.tmpl",
        "endpoint/api/${use_case_name}.py",
    ),
    (QUERY_MODULE, ENDPOINT_CLI): (
        "query_module/endpoint/cli/query.py.tmpl",
        "endpoint/cli/${use_case_name}.py",
    ),
    (QUERY_MODULE, ENDPOINT_WEB): (
        "query_module/endpoint/web/query.py.tmpl",
        "endpoint/web/${use_case_name}.py",
    ),
    (QUERY_MODULE, ENDPOINT_API): (
        "query_module/endpoint/api/query.py.tmpl",
        "endpoint/api/${use_case_name}.py",
    ),
}

# Application-layer file per module type (for feature generation).
_FEATURE_APPLICATION_FILE: dict[str, tuple[str, str]] = {
    COMMAND_MODULE: (
        "command_module/application/use_case.py.tmpl",
        "application/${use_case_name}.py",
    ),
    QUERY_MODULE: (
        "query_module/application/query.py.tmpl",
        "application/${use_case_name}.py",
    ),
}


def _to_pascal(name: str) -> str:
    """Convert snake_case name to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def _render(template_rel: str, variables: dict[str, str]) -> str:
    """Read and render a template file with the given variables."""
    tmpl_path = _TEMPLATES_DIR / template_rel
    source = tmpl_path.read_text(encoding="utf-8")
    return Template(source).substitute(variables)


def _resolve_output_path(path_template: str, variables: dict[str, str]) -> str:
    """Resolve an output path template with variables."""
    return Template(path_template).substitute(variables)


def _write(path: Path, content: str) -> None:
    """Write content to path, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _validate_endpoints(endpoints: list[str]) -> None:
    """Raise ValueError if any endpoint value is not recognised.

    Args:
        endpoints: Endpoint names to validate.

    Raises:
        ValueError: If any value is not in VALID_ENDPOINTS.
    """
    invalid = [i for i in endpoints if i not in VALID_ENDPOINTS]
    if invalid:
        valid_str = ", ".join(f"'{v}'" for v in VALID_ENDPOINTS)
        raise ValueError(
            f"Unknown endpoint(s): {invalid}. Valid values are: {valid_str}."
        )


def _read_module_type(module_path: Path) -> str:
    """Infer module type from existing __init__.py __modularity__ dict.

    Args:
        module_path: Path to the module root directory.

    Returns:
        Module type string (COMMAND_MODULE or QUERY_MODULE).

    Raises:
        FileNotFoundError: If __init__.py does not exist.
        ValueError: If __modularity__ dict is missing or type is unrecognised.
    """
    init_file = module_path / "__init__.py"
    if not init_file.exists():
        raise FileNotFoundError(
            f"No __init__.py found at {init_file}. "
            "Is this a valid abcdef module directory?"
        )

    source = init_file.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(init_file))
    modularity_dict = Modularity._extract_modularity_dict(tree)

    if modularity_dict is None:
        raise ValueError(
            f"{init_file}: no __modularity__ declaration found. "
            "Cannot infer module type."
        )

    module_type = modularity_dict.get("type")
    if module_type not in (COMMAND_MODULE, QUERY_MODULE):
        raise ValueError(
            f"{init_file}: __modularity__['type'] is '{module_type}', "
            f"expected '{COMMAND_MODULE}' or '{QUERY_MODULE}'."
        )

    return module_type  # type: ignore[return-value]


def generate_module(
    name: str,
    module_type: str,
    root: Path,
    endpoints: list[str] | None = None,
) -> list[Path]:
    """Scaffold a new module directory tree under root.

    Args:
        name: Module name in snake_case (e.g. 'orders').
        module_type: COMMAND_MODULE or QUERY_MODULE constant.
        root: Root directory to create the module under.
        endpoints: Endpoint types to scaffold (default: ['cli']).
            Valid values: 'cli', 'web', 'api'.

    Returns:
        List of created file paths.

    Raises:
        ValueError: If module_type or any endpoint value is invalid.
        FileExistsError: If <root>/<name> already exists.
    """
    if module_type not in (COMMAND_MODULE, QUERY_MODULE):
        raise ValueError(
            f"module_type must be '{COMMAND_MODULE}' or '{QUERY_MODULE}', "
            f"got '{module_type}'."
        )

    resolved_endpoints = endpoints if endpoints is not None else [ENDPOINT_CLI]
    _validate_endpoints(resolved_endpoints)

    module_dir = root / name
    if module_dir.exists():
        raise FileExistsError(
            f"Directory already exists: {module_dir}. Refusing to overwrite."
        )

    pascal = _to_pascal(name)
    variables = {
        "module_name": name,
        "module_name_pascal": pascal,
        "module_type": module_type,
        "aggregate_pascal": pascal,
        "aggregate_pascal_id": f"{pascal}Id",
        "aggregate_pascal_repository": f"{pascal}Repository",
        "document_pascal": f"{pascal}Document",
        "use_case_name": "placeholder",
        "use_case_pascal": "Placeholder",
    }

    base_files = (
        _COMMAND_MODULE_BASE_FILES
        if module_type == COMMAND_MODULE
        else _QUERY_MODULE_BASE_FILES
    )

    file_specs: list[tuple[str, str]] = list(base_files)
    for iface in resolved_endpoints:
        file_specs.append(_MODULE_ENDPOINT_FILES[(module_type, iface)])

    created: list[Path] = []
    for tmpl_rel, out_rel in file_specs:
        resolved_out = _resolve_output_path(out_rel, variables)
        out_path = module_dir / resolved_out
        content = _render(tmpl_rel, variables)
        _write(out_path, content)
        created.append(out_path)

    return created


def generate_feature(
    module_name: str,
    use_case_name: str,
    root: Path,
    endpoints: list[str] | None = None,
) -> list[Path]:
    """Add a use-case feature to an existing module.

    Creates:
    - application/<use_case_name>.py
    - endpoint/<type>/<use_case_name>.py for each requested endpoint

    Does not modify __init__.py — export wiring is manual.

    Args:
        module_name: Name of the existing module (snake_case).
        use_case_name: Name of the use case (snake_case, e.g. 'create_order').
        root: Root directory containing the module.
        endpoints: Endpoint types to scaffold (default: ['cli']).
            Valid values: 'cli', 'web', 'api'.

    Returns:
        List of created file paths.

    Raises:
        FileNotFoundError: If the module directory does not exist.
        FileExistsError: If any target file already exists.
        ValueError: If module type cannot be determined or endpoint is invalid.
    """
    resolved_endpoints = endpoints if endpoints is not None else [ENDPOINT_CLI]
    _validate_endpoints(resolved_endpoints)

    module_dir = root / module_name
    if not module_dir.exists():
        raise FileNotFoundError(
            f"Module directory not found: {module_dir}. Run 'abcdef-gen module' first."
        )

    module_type = _read_module_type(module_dir)
    module_pascal = _to_pascal(module_name)
    use_case_pascal = _to_pascal(use_case_name)

    variables = {
        "module_name": module_name,
        "module_name_pascal": module_pascal,
        "module_type": module_type,
        "aggregate_pascal": module_pascal,
        "aggregate_pascal_id": f"{module_pascal}Id",
        "aggregate_pascal_repository": f"{module_pascal}Repository",
        "document_pascal": f"{module_pascal}Document",
        "use_case_name": use_case_name,
        "use_case_pascal": use_case_pascal,
    }

    app_tmpl, app_out = _FEATURE_APPLICATION_FILE[module_type]
    file_specs: list[tuple[str, str]] = [(app_tmpl, app_out)]
    for iface in resolved_endpoints:
        file_specs.append(_FEATURE_ENDPOINT_FILES[(module_type, iface)])

    # Check for existing files before writing any.
    planned: list[tuple[str, Path]] = []
    for tmpl_rel, out_rel in file_specs:
        resolved_out = _resolve_output_path(out_rel, variables)
        out_path = module_dir / resolved_out
        if out_path.exists():
            raise FileExistsError(
                f"File already exists: {out_path}. Refusing to overwrite."
            )
        planned.append((tmpl_rel, out_path))

    created: list[Path] = []
    for tmpl_rel, out_path in planned:
        content = _render(tmpl_rel, variables)
        _write(out_path, content)
        created.append(out_path)

    return created
