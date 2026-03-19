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

    assert len(violations) == 1
    v = violations[0]
    assert v.violation_type == "read_write_constraint"
    assert v.module_name == decl.name
    assert "get_x" in v.message
    assert "command" in v.message.lower()
    assert v.location == str(module_path / "__init__.py")


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

    assert len(violations) == 1
    v = violations[0]
    assert v.violation_type == "read_write_constraint"
    assert v.module_name == decl.name
    assert "do_x" in v.message
    assert "query" in v.message.lower()
    assert v.location == str(module_path / "__init__.py")


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

    assert len(violations) == 1
    v = violations[0]
    assert v.violation_type == "facade_rule"
    assert v.module_name == decl.name
    assert "other.app" in v.message
    assert v.location == str(init_file)


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

    name_map = {this_path: this_decl.name, other_path: other_decl.name}

    def fake_module_name(self: BoundaryValidator, path: Path) -> str:
        return name_map.get(path, path.name)

    monkeypatch.setattr(BoundaryValidator, "_module_name_from_path", fake_module_name)

    validator = BoundaryValidator([this_module, other_module])
    violations = validator.validate()

    assert len(violations) == 1
    v = violations[0]
    assert v.violation_type == "import_boundary"
    assert v.module_name == this_decl.name
    assert "other.mod.internals" in v.message
    assert str(Path("layer") / "impl.py") in v.location


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


def test_facade_rule_allows_abcdef_prefixed_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """abcdef.* imports in __init__.py are never flagged as facade violations."""
    module_path = tmp_path / "my_mod"
    module_path.mkdir()
    init_file = module_path / "__init__.py"
    init_file.write_text("from abcdef.c.markers import command\n", encoding="utf-8")

    decl = ModuleDeclaration(module_type="command_module", name="my.mod")
    api = _public_api_with()
    module = CommandModule(_declaration=decl, _path=module_path, _public_api=api)

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: "my.mod",
    )

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert not any(v.violation_type == "facade_rule" for v in violations)


def test_import_boundaries_allows_abcdef_prefixed_imports(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """abcdef.* imports in layer files are never flagged as import_boundary."""
    this_path = tmp_path / "my_mod"
    this_path.mkdir()
    (this_path / "application").mkdir()
    layer_file = this_path / "application" / "handler.py"
    layer_file.write_text(
        "from abcdef.c.command_handler import CommandHandler\n", encoding="utf-8"
    )

    decl = ModuleDeclaration(module_type="command_module", name="my.mod")
    module = CommandModule(
        _declaration=decl, _path=this_path, _public_api=PublicApi.empty()
    )

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: "my.mod",
    )

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert not any(v.violation_type == "import_boundary" for v in violations)


def test_facade_rule_allows_own_sub_namespace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Imports from own sub-namespace (e.g. mod.domain) are not facade violations."""
    module_path = tmp_path / "orders"
    module_path.mkdir()
    init_file = module_path / "__init__.py"
    init_file.write_text("from orders.domain.orders import Orders\n", encoding="utf-8")

    decl = ModuleDeclaration(module_type="command_module", name="orders")
    api = _public_api_with()
    module = CommandModule(_declaration=decl, _path=module_path, _public_api=api)

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: "orders",
    )

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert not any(v.violation_type == "facade_rule" for v in violations)


def test_import_boundaries_continue_past_init_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scanning continues past __init__.py and still detects later violations."""
    this_path = tmp_path / "this_mod"
    this_path.mkdir()
    layer_dir = this_path / "application"
    layer_dir.mkdir()

    # __init__.py at the layer root — must be skipped, not break the loop.
    (layer_dir / "__init__.py").write_text("", encoding="utf-8")

    # A sibling file with a real violation — must still be found.
    (layer_dir / "handler.py").write_text(
        "from other.mod.internals import X\n", encoding="utf-8"
    )

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

    name_map = {this_path: this_decl.name, other_path: other_decl.name}

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: name_map.get(path, path.name),
    )

    validator = BoundaryValidator([this_module, other_module])
    violations = validator.validate()

    assert any(v.violation_type == "import_boundary" for v in violations)


def test_facade_rule_continue_past_abcdef_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scanning continues past an abcdef.* import; still detects a later violation."""
    module_path = tmp_path / "my_mod"
    module_path.mkdir()
    init_file = module_path / "__init__.py"
    # First import is abcdef.* (must be skipped); second is a genuine foreign import.
    init_file.write_text(
        "from abcdef.c.markers import command\nfrom other.foreign import Something\n",
        encoding="utf-8",
    )

    decl = ModuleDeclaration(module_type="command_module", name="my.mod")
    module = CommandModule(
        _declaration=decl, _path=module_path, _public_api=_public_api_with()
    )

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: "my.mod",
    )

    validator = BoundaryValidator([module])
    violations = validator.validate()

    assert any(v.violation_type == "facade_rule" for v in violations)


def test_import_boundaries_abcdef_prefixed_module_not_flagged(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Imports from a registered module whose name starts with 'abcdef' are excluded.

    This is the only scenario where the startswith("abcdef") guard in
    _validate_import_boundaries can be meaningfully distinguished from a broken
    guard string: a module named "abcdef.foo" is registered, and a layer file
    imports from its internals. The real guard skips the import; a broken guard
    would produce a spurious import_boundary violation.
    """
    this_path = tmp_path / "this_mod"
    this_path.mkdir()
    (this_path / "application").mkdir()
    (this_path / "application" / "handler.py").write_text(
        "from abcdef.foo.internals import X\n", encoding="utf-8"
    )

    abcdef_foo_path = tmp_path / "abcdef_foo"
    abcdef_foo_path.mkdir()

    this_decl = ModuleDeclaration(module_type="command_module", name="this.mod")
    abcdef_foo_decl = ModuleDeclaration(module_type="query_module", name="abcdef.foo")

    this_module = CommandModule(
        _declaration=this_decl, _path=this_path, _public_api=PublicApi.empty()
    )
    abcdef_foo_module = QueryModule(
        _declaration=abcdef_foo_decl,
        _path=abcdef_foo_path,
        _public_api=PublicApi.empty(),
    )

    name_map = {this_path: this_decl.name, abcdef_foo_path: abcdef_foo_decl.name}

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: name_map.get(path, path.name),
    )

    validator = BoundaryValidator([this_module, abcdef_foo_module])
    violations = validator.validate()

    assert not any(v.violation_type == "import_boundary" for v in violations)


def test_import_boundaries_continue_past_abcdef_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Inner loop continues past abcdef.* import and still detects later violations.

    Covers the continue->break mutant in the abcdef guard inside the per-node loop:
    the file has an abcdef.* import first (skipped), then a deep import into a known
    module (violation). If the guard used break instead of continue, the violation
    would be missed.
    """
    this_path = tmp_path / "this_mod"
    this_path.mkdir()
    (this_path / "application").mkdir()
    (this_path / "application" / "handler.py").write_text(
        "from abcdef.c.markers import command\nfrom other.mod.internals import X\n",
        encoding="utf-8",
    )

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

    name_map = {this_path: this_decl.name, other_path: other_decl.name}

    monkeypatch.setattr(
        BoundaryValidator,
        "_module_name_from_path",
        lambda self, path: name_map.get(path, path.name),
    )

    validator = BoundaryValidator([this_module, other_module])
    violations = validator.validate()

    assert any(v.violation_type == "import_boundary" for v in violations)
