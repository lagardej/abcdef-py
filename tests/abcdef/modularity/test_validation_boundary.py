"""Tests for BoundaryValidator — read/write, facade, and import-boundary rules."""

from pathlib import Path

import pytest

from abcdef.modularity.module import CommandModule, ModuleDeclaration, QueryModule
from abcdef.modularity.validation import PublicApi, PublicApiSymbol
from abcdef.modularity.validation_boundary import BoundaryValidator


def _public_api_with(
    symbols: tuple[PublicApiSymbol, ...] = (),
    commands: tuple[PublicApiSymbol, ...] = (),
    queries: tuple[PublicApiSymbol, ...] = (),
) -> PublicApi:
    return PublicApi(
        symbols=frozenset(symbols),
        commands=frozenset(commands),
        queries=frozenset(queries),
        events=frozenset(),
        spis=frozenset(),
    )


def test_read_write_constraints_command_exports_query(tmp_path: Path) -> None:
    """Command module that exposes a query produces a read_write_constraint."""
    module_path = tmp_path / "cmd_module"
    module_path.mkdir()
    decl = ModuleDeclaration(module_type="command_module", name="app.commands")

    query_sym = PublicApiSymbol(
        name="get_x", kind="query", full_path="app.commands.get_x"
    )
    api = _public_api_with(queries=(query_sym,))

    module = CommandModule(_declaration=decl, _path=module_path, _public_api=api)

    validator = BoundaryValidator([module])

    violations = validator.validate()

    assert any(
        v.violation_type == "read_write_constraint" and v.module_name == decl.name
        for v in violations
    )


def test_read_write_constraints_query_exports_command(tmp_path: Path) -> None:
    """Query module that exposes a command produces a read_write_constraint."""
    module_path = tmp_path / "qry_module"
    module_path.mkdir()
    decl = ModuleDeclaration(module_type="query_module", name="app.queries")

    cmd_sym = PublicApiSymbol(name="do_x", kind="command", full_path="app.queries.do_x")
    api = _public_api_with(commands=(cmd_sym,))

    module = QueryModule(_declaration=decl, _path=module_path, _public_api=api)

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert any(
        v.violation_type == "read_write_constraint" and v.module_name == decl.name
        for v in violations
    )


def test_facade_rule_reexports_foreign_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Module __init__.py that re-exports from a foreign app module is a facade_rule."""
    module_path = tmp_path / "facade_mod"
    module_path.mkdir()
    init_file = module_path / "__init__.py"
    init_file.write_text("from other.app import something\n", encoding="utf-8")

    decl = ModuleDeclaration(module_type="command_module", name="facade.mod")
    api = _public_api_with()
    module = CommandModule(_declaration=decl, _path=module_path, _public_api=api)

    name_map = {module_path: decl.name}

    def fake_module_name(self: BoundaryValidator, path: Path) -> str:
        return name_map.get(path, path.name)

    monkeypatch.setattr(BoundaryValidator, "_module_name_from_path", fake_module_name)

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert any(
        v.violation_type == "facade_rule" and v.module_name == decl.name
        for v in violations
    )


def test_import_boundaries_detect_internal_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Layer file importing module internals produces an import_boundary violation."""
    this_path = tmp_path / "this_mod"
    this_path.mkdir()
    (this_path / "layer").mkdir()
    impl_file = this_path / "layer" / "impl.py"
    impl_file.write_text("from other.mod.internals import X\n", encoding="utf-8")

    other_path = tmp_path / "other_mod"
    other_path.mkdir()

    this_decl = ModuleDeclaration(module_type="command_module", name="this.mod")
    other_decl = ModuleDeclaration(module_type="query_module", name="other.mod")

    this_module = CommandModule(
        _declaration=this_decl, _path=this_path, _public_api=PublicApi.empty()
    )
    other_module = QueryModule(
        _declaration=other_decl, _path=other_path, _public_api=PublicApi.empty()
    )

    # Map paths to logical module names for deterministic name comparison.
    name_map = {this_path: this_decl.name, other_path: other_decl.name}

    def fake_module_name(self: BoundaryValidator, path: Path) -> str:
        return name_map.get(path, path.name)

    monkeypatch.setattr(BoundaryValidator, "_module_name_from_path", fake_module_name)

    validator = BoundaryValidator([this_module, other_module])
    violations = validator.validate()

    # Should detect an import_boundary violation for the deep import.
    assert any(
        v.violation_type == "import_boundary" and v.module_name == this_decl.name
        for v in violations
    )


def test_import_boundaries_allow_root_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Importing from a module root raises no import_boundary violation."""
    this_path = tmp_path / "this_mod2"
    this_path.mkdir()
    (this_path / "layer").mkdir()
    impl_file = this_path / "layer" / "impl.py"
    impl_file.write_text("from other.mod import X\n", encoding="utf-8")

    other_path = tmp_path / "other_mod2"
    other_path.mkdir()

    this_decl = ModuleDeclaration(module_type="command_module", name="this.mod2")
    other_decl = ModuleDeclaration(module_type="query_module", name="other.mod2")

    this_module = CommandModule(
        _declaration=this_decl, _path=this_path, _public_api=PublicApi.empty()
    )
    other_module = QueryModule(
        _declaration=other_decl, _path=other_path, _public_api=PublicApi.empty()
    )

    name_map = {this_path: this_decl.name, other_path: other_decl.name}

    def fake_module_name(self: BoundaryValidator, path: Path) -> str:
        return name_map.get(path, path.name)

    monkeypatch.setattr(BoundaryValidator, "_module_name_from_path", fake_module_name)

    validator = BoundaryValidator([this_module, other_module])
    violations = validator.validate()

    assert all(v.violation_type != "import_boundary" for v in violations)
