# Contributing to ABCDEF

## Prerequisites

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) for dependency management and running tools

All commands below use `uv run`. No global installs are required.

---

## Running tests

### With Make (Unix / macOS)

```bash
make test        # run pytest with coverage (default verbosity)
make test V=0    # quiet — failures only
make test V=2    # verbose — per-test names, full tracebacks
```

### Without Make (Windows and Unix)

```bash
uv run pytest                          # normal output
uv run pytest -q                       # quiet
uv run pytest -v                       # verbose
```

`make` is optional. All targets are thin wrappers around `uv run` commands and can be
run directly on any platform.

---

## Coverage

Coverage is reported automatically after every test run. To see a summary with missing
lines:

```bash
uv run pytest --cov=abcdef --cov-report=term-missing
```

This is the default — `pyproject.toml` configures it via `addopts`.

Branch coverage is enabled. The project targets high coverage but accepts that
`pass`/`...` bodies in `@abstractmethod` definitions are structurally unreachable and
will appear as misses.

---

## Linting and formatting

```bash
make lint          # check for lint violations (no changes)
make check-format  # check formatting (no changes)
make fix           # auto-fix lint violations
make format        # auto-format source files
```

Without Make:

```bash
uv run ruff check .          # lint
uv run ruff format --check . # check formatting
uv run ruff check --fix .    # auto-fix
uv run ruff format .         # format
```

---

## Type checking

```bash
make check-types
# or
uv run pyright
```

---

## Full CI check

Runs format check, lint, type check, and tests in sequence:

```bash
make ci
# or run each step individually (see above)
```

---

## Logs

`make test`, `make ci`, and `make mutate` write timestamped logs to `logs/`. The
symlinks `logs/test.log`, `logs/ci.log`, and `logs/mutate.log` always point to the
latest run.
