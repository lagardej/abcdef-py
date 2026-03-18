#!/usr/bin/env python3
r"""Show mutmut diffs for stable surviving mutants across multiple runs.

Usage:
    # Show survivors from a single run (original behaviour)
    uv run python scripts/mutmut_show_survivors.py <pattern> [output_file]

    # Show survivors stable across N runs (intersection mode)
    uv run python scripts/mutmut_show_survivors.py <pattern> [output_file] \
        --logs <log1> <log2> ...

    # Show survivors appearing in at least M of N logs (threshold mode)
    uv run python scripts/mutmut_show_survivors.py <pattern> [output_file] \
        --logs <log1> <log2> ... --min-runs 2

Examples:
    # Single run — query mutmut results directly
    uv run python scripts/mutmut_show_survivors.py \
        validation_boundary logs/survivors_vb.log

    # Intersection across 4 logs — only survivors present in all 4
    uv run python scripts/mutmut_show_survivors.py \
        validation_boundary logs/survivors_vb_stable.log \
        --logs logs/mutate-1.log logs/mutate-2.log \
               logs/mutate-3.log logs/mutate-4.log

    # At least 3 of 4 runs
    uv run python scripts/mutmut_show_survivors.py \
        validation_boundary logs/survivors_vb_stable.log \
        --logs logs/mutate-1.log logs/mutate-2.log \
               logs/mutate-3.log logs/mutate-4.log --min-runs 3

The script:
  1a. If --logs is given: parses survivor lists from each log file and computes
      the intersection (or threshold subset). These logs are the raw mutmut output
      files produced by `make mutate`.
  1b. Otherwise: runs `mutmut results` live to get the current survivor list.
  2. Filters by the given module pattern (substring match on mutant ID).
  3. Runs `mutmut show <id>` for each stable survivor and collects the diffs.
  4. Writes the result to stdout or the given output file.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections import Counter
from pathlib import Path


def survivors_from_log(log_path: Path, pattern: str) -> set[str]:
    """Parse a mutmut log file and return surviving mutant IDs matching pattern."""
    survivors: set[str] = set()
    try:
        text = log_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"Warning: cannot read {log_path}: {e}", file=sys.stderr)
        return survivors

    for line in text.splitlines():
        line = line.strip()
        # Survivor lines look like:
        #   abcdef.some.module.xǁClassǁmethod__mutmut_N: survived
        if ": survived" not in line:
            continue
        mutant_id = line.split(":")[0].strip()
        if pattern in mutant_id:
            survivors.add(mutant_id)
    return survivors


def survivors_from_mutmut(pattern: str) -> set[str]:
    """Run `mutmut results` and return surviving mutant IDs matching pattern."""
    result = subprocess.run(
        ["mutmut", "results"],
        capture_output=True,
        text=True,
        check=True,
    )
    survivors: set[str] = set()
    for line in result.stdout.splitlines():
        mutant_id = line.strip().split(":")[0].strip()
        if not mutant_id:
            continue
        if pattern in mutant_id:
            survivors.add(mutant_id)
    return survivors


def show_mutant(mutant_id: str) -> str:
    """Return the diff output for a single mutant."""
    result = subprocess.run(
        ["mutmut", "show", mutant_id],
        capture_output=True,
        text=True,
    )
    return result.stdout or result.stderr


def stable_survivors(
    log_paths: list[Path],
    pattern: str,
    min_runs: int,
) -> tuple[list[str], dict[str, int]]:
    """Return mutant IDs that survived in at least min_runs of the given logs.

    Returns (stable_ids_sorted, counts_by_id).
    """
    counts: Counter[str] = Counter()
    for log_path in log_paths:
        for mutant_id in survivors_from_log(log_path, pattern):
            counts[mutant_id] += 1

    stable = sorted(
        (mid for mid, count in counts.items() if count >= min_runs),
        key=lambda mid: (-counts[mid], mid),  # most-frequent first
    )
    return stable, dict(counts)


def main() -> None:
    """Parse arguments and run the survivor diff report."""
    parser = argparse.ArgumentParser(
        description="Show mutmut diffs for stable survivors across runs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("pattern", help="Module pattern to filter (substring match)")
    parser.add_argument("output", nargs="?", help="Output file path (default: stdout)")
    parser.add_argument(
        "--logs",
        nargs="+",
        metavar="LOG",
        help="Mutate log files to intersect. If omitted, queries mutmut results live.",
    )
    parser.add_argument(
        "--min-runs",
        type=int,
        default=None,
        help=(
            "Minimum number of runs a mutant must survive to be reported. "
            "Defaults to len(logs) (full intersection) when --logs is given."
        ),
    )
    args = parser.parse_args()

    pattern: str = args.pattern
    output_path: Path | None = Path(args.output) if args.output else None

    # --- Determine stable survivors ---
    counts: dict[str, int] = {}

    if args.logs:
        log_paths = [Path(p) for p in args.logs]
        n_logs = len(log_paths)
        min_runs = args.min_runs if args.min_runs is not None else n_logs
        survivors, counts = stable_survivors(log_paths, pattern, min_runs)
        mode_desc = (
            f"appearing in at least {min_runs}/{n_logs} runs"
            if min_runs < n_logs
            else f"appearing in all {n_logs} runs (intersection)"
        )
    else:
        survivors = sorted(survivors_from_mutmut(pattern))
        min_runs = 1
        mode_desc = "from current mutmut results"

    # --- Build output ---
    lines: list[str] = []

    if not survivors:
        lines.append(f"No surviving mutants found matching {pattern!r} {mode_desc}.\n")
    else:
        lines.append(
            f"Stable survivors matching {pattern!r} {mode_desc}: {len(survivors)}\n"
        )
        lines.append("=" * 72 + "\n\n")

        for mutant_id in survivors:
            run_count = counts.get(mutant_id, 1)
            total = len(args.logs) if args.logs else 1
            lines.append(f"=== {mutant_id} (survived {run_count}/{total} runs) ===\n")
            lines.append(show_mutant(mutant_id))
            lines.append("\n")

    output = "".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
        print(
            f"Written to {output_path} ({len(survivors)} stable survivors {mode_desc})"
        )
    else:
        print(output, end="")


if __name__ == "__main__":
    main()
