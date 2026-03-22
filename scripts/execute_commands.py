#!/usr/bin/env python3
"""Execute bash commands from .abcdef/commands.sh.

Reads commands from .abcdef/commands.sh and executes them in order.
Output is logged to logs/commands-TIMESTAMP.log
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def main() -> None:
    """Execute commands from .abcdef/commands.sh."""
    project_root = Path.cwd()
    commands_file = project_root / ".abcdef" / "commands.sh"
    logs_dir = project_root / "logs"

    if not commands_file.exists():
        print(f"Error: {commands_file} not found", file=sys.stderr)
        sys.exit(1)

    # Ensure logs directory exists
    logs_dir.mkdir(exist_ok=True)

    # Read commands
    commands_text = commands_file.read_text(encoding="utf-8").strip()
    commands = commands_text.split("\n")

    # Filter out empty lines and comments
    commands = [
        cmd.strip()
        for cmd in commands
        if cmd.strip() and not cmd.strip().startswith("#")
    ]

    if not commands:
        print("No commands to execute")
        return

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = logs_dir / f"commands-{timestamp}.log"

    print(f"Executing {len(commands)} commands from {commands_file}")
    print(f"Logging output to {log_file}\n")

    with Path.open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Executing commands from {commands_file}\n")
        log.write(f"{'=' * 60}\n\n")

        for i, cmd in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] {cmd}")
            log.write(f"[{i}/{len(commands)}] {cmd}\n")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            if result.stdout:
                log.write(result.stdout)
            if result.stderr:
                log.write(result.stderr)

            if result.returncode != 0:
                log.write(f"[ERROR] Exit code: {result.returncode}\n")
                print(f"  ❌ Failed (exit code {result.returncode})")
            else:
                print("  ✓ Success")

            log.write(f"\n{'-' * 60}\n\n")

    print(f"\nDone! See {log_file} for details")


if __name__ == "__main__":
    main()
