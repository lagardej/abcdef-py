"""CLI entry point for abcdef-gen scaffolding tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from abcdef.codegen.generator import VALID_ENDPOINTS, generate_feature, generate_module
from abcdef.modularity.markers import COMMAND_MODULE, QUERY_MODULE


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="abcdef-gen",
        description="Scaffold abcdef modules and features.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # module sub-command
    module_cmd = sub.add_parser(
        "module",
        help="Scaffold a new module directory tree.",
    )
    module_cmd.add_argument("name", help="Module name in snake_case (e.g. orders).")
    module_cmd.add_argument(
        "--type",
        dest="module_type",
        choices=[COMMAND_MODULE, QUERY_MODULE],
        required=True,
        help="Module type: command or query.",
    )
    module_cmd.add_argument(
        "--endpoints",
        nargs="+",
        choices=list(VALID_ENDPOINTS),
        default=["cli"],
        metavar="ENDPOINT",
        help=(
            "Endpoint types to scaffold (default: cli). "
            f"Choices: {', '.join(VALID_ENDPOINTS)}. "
            "Multiple values accepted."
        ),
    )
    module_cmd.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory to create the module under (default: cwd).",
    )

    # feature sub-command
    feature_cmd = sub.add_parser(
        "feature",
        help="Add a use-case feature to an existing module.",
    )
    feature_cmd.add_argument("module", help="Name of the existing module (snake_case).")
    feature_cmd.add_argument(
        "use_case", help="Use-case name in snake_case (e.g. create_order)."
    )
    feature_cmd.add_argument(
        "--endpoints",
        nargs="+",
        choices=list(VALID_ENDPOINTS),
        default=["cli"],
        metavar="ENDPOINT",
        help=(
            "Endpoint types to scaffold (default: cli). "
            f"Choices: {', '.join(VALID_ENDPOINTS)}. "
            "Multiple values accepted."
        ),
    )
    feature_cmd.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Root directory containing the module (default: cwd).",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for abcdef-gen.

    Args:
        argv: Argument list (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.root or Path.cwd()

    try:
        if args.command == "module":
            created = generate_module(
                name=args.name,
                module_type=args.module_type,
                root=root,
                endpoints=args.endpoints,
            )
            print(
                f"Created module '{args.name}' ({args.module_type}) "
                f"[endpoints: {', '.join(args.endpoints)}]:"
            )
            for path in created:
                print(f"  {path}")

        elif args.command == "feature":
            created = generate_feature(
                module_name=args.module,
                use_case_name=args.use_case,
                root=root,
                endpoints=args.endpoints,
            )
            print(
                f"Added feature '{args.use_case}' to module '{args.module}' "
                f"[endpoints: {', '.join(args.endpoints)}]:"
            )
            for path in created:
                print(f"  {path}")

    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
