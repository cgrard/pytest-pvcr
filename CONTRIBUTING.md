# Contributing to pytest-pvcr

## Development Setup

Fork the repository and clone your fork:

```bash
git clone https://github.com/<owner>/pytest-pvcr.git
cd pytest-pvcr
uv sync
```

Python 3.12+ required.

## Running Tests

```bash
uv run pytest                # All tests
uv run pytest tests/ -v      # Verbose
uv run pytest --cov --cov-report=term-missing  # With coverage
```

## Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```text
type(scope): description
```

Types: `feat`, `fix`, `docs`, `refactor`, `chore`, `test`
Scopes: `plugin`, `wrapper`, `recordings`, `ci`, `tests`, `project`

## Test Coverage

Current coverage: **67%** (threshold: 65%)

| File | Coverage | Notes |
| ---- | -------- | ----- |
| `plugin.py` | 50% | Module loaded before coverage starts (pytester runs a subprocess). Imports, hooks, and fixtures are not measured. |
| `wrapper.py` | 60% | Same early-load issue. The explicit `stdout`/`stderr` fallback branch (lines 61-62) and `MetaSubprocessWrapper.__getattribute__` are not covered. |
| `recordings.py` | 77% | Some branches untested: `write()` in `all` mode replacing an existing entry, `clean(write=True)` deleting the file, and some fuzzy compiler edge cases. |

### Quick wins to improve coverage

- Test `subprocess.run()` with explicit `stdout`/`stderr` arguments (covers `wrapper.py` lines 61-62)
- Test `Recordings.clean(write=True)` when a recording file exists (covers `recordings.py` file deletion)
- Test `write()` in `all` mode replacing an already-recorded command (covers `recordings.py` slice replacement)

## Roadmap

### Tests

- [ ] Add edge case tests for `wrapper.py`: empty args, special characters, large stdin/stdout
- [ ] Add tests for combining multiple CLI flags (`--pvcr-block-run` + `--pvcr-record-mode`, etc.)
- [ ] Add tests for explicit `stdout`/`stderr` arguments to `subprocess.run()`
- [ ] Add tests for invalid fuzzy matcher regexes
- [ ] Add tests for corrupted/malformed YAML recording files
- [ ] Add tests for Unicode/non-ASCII subprocess output
- [ ] Improve coverage of `plugin.py` (currently 50%, limited by pytest plugin import order — structural limitation)

### Features

- [ ] Support `subprocess.Popen`, `check_output`, and `check_call`
- [ ] Thread-safety for `pytest-xdist` compatibility (global state on metaclass)
- [ ] Error-level logging for actual failures (currently only debug/warning)

### Documentation

- [ ] Document the YAML recording file format and base64 encoding
- [ ] Document the `pvcr` logger for debugging (`logging.getLogger("pvcr")`)
- [ ] Add examples of advanced fuzzy matching patterns
- [ ] Document iteration tracking for repeated commands
- [ ] Add a troubleshooting section to the README

### Infrastructure

- [ ] Add pre-commit hooks configuration
