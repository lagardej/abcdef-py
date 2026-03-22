#!/usr/bin/env python3
"""Execute bash commands from .abcdef/commands.sh.

Reads commands from .abcdef/commands.sh and executes them in order.
Output is logged to logs/commands-TIMESTAMP.log

Supports:
- Single-line commands
- Multi-line git commit messages with git commit -m "..." syntax
- Line continuations with backslash
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_commands(text: str) -> list[str]:
    """Parse commands from text, handling multi-line git commit messages.
    
    Handles:
    - Regular single-line commands
    - git commit -m "..." with multi-line messages (quoted strings preserve newlines)
    - Line continuations with backslash
    """
    commands = []
    current_cmd = ""
    in_quote = False
    quote_char = None
    i = 0
    
    lines = text.split("\n")
    line_idx = 0
    
    while line_idx < len(lines):
        line = lines[line_idx]
        
        # Skip empty lines and comments (at start of line, not in quotes)
        if not line.strip() or (not in_quote and line.strip().startswith("#")):
            line_idx += 1
            continue
        
        # Process character by character to handle quotes
        for char_idx, char in enumerate(line):
            if char in ('"', "'") and (char_idx == 0 or line[char_idx - 1] != "\\"):
                if not in_quote:
                    in_quote = True
                    quote_char = char
                elif char == quote_char:
                    in_quote = False
                    quote_char = None
            
            current_cmd += char
        
        # Check if line continues (ends with backslash outside quotes)
        if not in_quote and line.rstrip().endswith("\\"):
            current_cmd = current_cmd.rstrip()[:-1]  # Remove trailing backslash
            current_cmd += "\n"
        elif in_quote:
            # We're in a multi-line quoted string, add newline
            current_cmd += "\n"
        else:
            # End of command
            if current_cmd.strip():
                commands.append(current_cmd.strip())
            current_cmd = ""
        
        line_idx += 1
    
    # Handle any remaining command
    if current_cmd.strip():
        commands.append(current_cmd.strip())
    
    return commands


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

    # Read and parse commands
    commands_text = commands_file.read_text(encoding="utf-8")
    commands = parse_commands(commands_text)

    if not commands:
        print("No commands to execute")
        return

    # Create timestamped log file
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = logs_dir / f"commands-{timestamp}.log"

    print(f"Executing {len(commands)} command(s) from {commands_file}")
    print(f"Logging output to {log_file}\n")

    with Path.open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Executing commands from {commands_file}\n")
        log.write(f"{'=' * 60}\n\n")

        for i, cmd in enumerate(commands, 1):
            # Display command (truncate if very long, handle multi-line)
            display_cmd = cmd.replace("\n", " \\n ")
            if len(display_cmd) > 60:
                display_cmd = display_cmd[:57] + "..."
            
            print(f"[{i}/{len(commands)}] {display_cmd}")
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
