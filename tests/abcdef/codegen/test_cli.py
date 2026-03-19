"""Tests for abcdef.codegen.cli — CLI entry point."""

from pathlib import Path

import pytest

from abcdef.codegen.cli import main
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE


class TestModuleCommand:
    """Tests for the 'module' sub-command."""

    def test_module_command_returns_zero(self, tmp_path: Path) -> None:
        """Successful module command exits with code 0."""
        rc = main(
            ["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)]
        )

        assert rc == 0

    def test_module_command_creates_directory(self, tmp_path: Path) -> None:
        """Module command creates the module directory."""
        main(["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)])

        assert (tmp_path / "orders").is_dir()

    def test_module_command_creates_init(self, tmp_path: Path) -> None:
        """Module command creates __init__.py."""
        main(["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)])

        assert (tmp_path / "orders" / "__init__.py").exists()

    def test_module_command_query_type(self, tmp_path: Path) -> None:
        """Module command accepts query type."""
        rc = main(
            ["module", "reports", "--type", QUERY_MODULE, "--root", str(tmp_path)]
        )

        assert rc == 0
        assert (tmp_path / "reports" / "__init__.py").exists()

    def test_module_command_existing_dir_returns_one(self, tmp_path: Path) -> None:
        """Module command returns exit code 1 if directory already exists."""
        (tmp_path / "orders").mkdir()

        rc = main(
            ["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)]
        )

        assert rc == 1

    def test_module_command_prints_created_files(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Module command prints list of created files to stdout."""
        main(["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)])

        out = capsys.readouterr().out
        assert "orders" in out
        assert "__init__.py" in out

    def test_module_command_error_goes_to_stderr(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Module command writes error to stderr on failure."""
        (tmp_path / "orders").mkdir()

        main(["module", "orders", "--type", COMMAND_MODULE, "--root", str(tmp_path)])

        err = capsys.readouterr().err
        assert "Error" in err

    def test_module_command_invalid_type_exits_nonzero(self, tmp_path: Path) -> None:
        """Invalid --type value causes argparse to exit non-zero."""
        with pytest.raises(SystemExit) as exc_info:
            main(["module", "orders", "--type", "invalid", "--root", str(tmp_path)])

        assert exc_info.value.code != 0

    def test_module_command_missing_type_exits_nonzero(self, tmp_path: Path) -> None:
        """Missing --type causes argparse to exit non-zero."""
        with pytest.raises(SystemExit) as exc_info:
            main(["module", "orders", "--root", str(tmp_path)])

        assert exc_info.value.code != 0


class TestFeatureCommand:
    """Tests for the 'feature' sub-command."""

    def _scaffold(self, tmp_path: Path, name: str = "orders") -> None:
        """Scaffold a command module for feature tests."""
        main(["module", name, "--type", COMMAND_MODULE, "--root", str(tmp_path)])

    def test_feature_command_returns_zero(self, tmp_path: Path) -> None:
        """Successful feature command exits with code 0."""
        self._scaffold(tmp_path)

        rc = main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        assert rc == 0

    def test_feature_command_creates_files(self, tmp_path: Path) -> None:
        """Feature command creates application and CLI files."""
        self._scaffold(tmp_path)
        main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        assert (tmp_path / "orders" / "application" / "create_order.py").exists()
        assert (tmp_path / "orders" / "interface" / "cli" / "create_order.py").exists()

    def test_feature_command_missing_module_returns_one(self, tmp_path: Path) -> None:
        """Feature command returns exit code 1 if module dir does not exist."""
        rc = main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        assert rc == 1

    def test_feature_command_duplicate_returns_one(self, tmp_path: Path) -> None:
        """Feature command returns exit code 1 if feature already exists."""
        self._scaffold(tmp_path)
        main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        rc = main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        assert rc == 1

    def test_feature_command_prints_created_files(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Feature command prints list of created files to stdout."""
        self._scaffold(tmp_path)
        main(["feature", "orders", "create_order", "--root", str(tmp_path)])

        out = capsys.readouterr().out
        assert "create_order" in out

    def test_feature_command_missing_args_exits_nonzero(self) -> None:
        """Missing positional args causes argparse to exit non-zero."""
        with pytest.raises(SystemExit) as exc_info:
            main(["feature"])

        assert exc_info.value.code != 0


class TestInterfacesFlag:
    """Tests for --interfaces flag on both sub-commands."""

    def test_module_web_interface_flag(self, tmp_path: Path) -> None:
        """--interfaces web generates web stub."""
        rc = main(
            [
                "module",
                "orders",
                "--type",
                COMMAND_MODULE,
                "--interfaces",
                "web",
                "--root",
                str(tmp_path),
            ]
        )

        assert rc == 0
        assert (tmp_path / "orders" / "interface" / "web" / "placeholder.py").exists()

    def test_module_api_interface_flag(self, tmp_path: Path) -> None:
        """--interfaces api generates api stub."""
        rc = main(
            [
                "module",
                "orders",
                "--type",
                COMMAND_MODULE,
                "--interfaces",
                "api",
                "--root",
                str(tmp_path),
            ]
        )

        assert rc == 0
        assert (tmp_path / "orders" / "interface" / "api" / "placeholder.py").exists()

    def test_module_multiple_interfaces_flag(self, tmp_path: Path) -> None:
        """--interfaces cli web api generates all three stubs."""
        rc = main(
            [
                "module",
                "orders",
                "--type",
                COMMAND_MODULE,
                "--interfaces",
                "cli",
                "web",
                "api",
                "--root",
                str(tmp_path),
            ]
        )

        assert rc == 0
        assert (tmp_path / "orders" / "interface" / "cli" / "placeholder.py").exists()
        assert (tmp_path / "orders" / "interface" / "web" / "placeholder.py").exists()
        assert (tmp_path / "orders" / "interface" / "api" / "placeholder.py").exists()

    def test_module_invalid_interface_exits_nonzero(self, tmp_path: Path) -> None:
        """Invalid --interfaces value causes argparse to exit non-zero."""
        with pytest.raises(SystemExit) as exc_info:
            main(
                [
                    "module",
                    "orders",
                    "--type",
                    COMMAND_MODULE,
                    "--interfaces",
                    "graphql",
                    "--root",
                    str(tmp_path),
                ]
            )

        assert exc_info.value.code != 0

    def test_feature_web_interface_flag(self, tmp_path: Path) -> None:
        """--interfaces web on feature generates web stub."""
        main(
            [
                "module",
                "orders",
                "--type",
                COMMAND_MODULE,
                "--root",
                str(tmp_path),
            ]
        )
        rc = main(
            [
                "feature",
                "orders",
                "create_order",
                "--interfaces",
                "web",
                "--root",
                str(tmp_path),
            ]
        )

        assert rc == 0
        assert (tmp_path / "orders" / "interface" / "web" / "create_order.py").exists()

    def test_module_output_mentions_interfaces(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Module command output includes selected interface names."""
        main(
            [
                "module",
                "orders",
                "--type",
                COMMAND_MODULE,
                "--interfaces",
                "web",
                "api",
                "--root",
                str(tmp_path),
            ]
        )

        out = capsys.readouterr().out
        assert "web" in out
        assert "api" in out


class TestNoSubcommand:
    """Tests for invocation with no sub-command."""

    def test_no_subcommand_exits_nonzero(self) -> None:
        """No sub-command causes argparse to exit non-zero."""
        with pytest.raises(SystemExit) as exc_info:
            main([])

        assert exc_info.value.code != 0
