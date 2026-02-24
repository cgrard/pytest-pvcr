# Contributing to pytest-pvcr

## Development Setup

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

## Roadmap

### Tests

- [ ] Add edge case tests for `wrapper.py`: empty args, special characters, large stdin/stdout
- [ ] Add tests for combining multiple CLI flags (`--pvcr-block-run` + `--pvcr-record-mode`, etc.)
- [ ] Add tests for invalid fuzzy matcher regexes
- [ ] Add tests for corrupted/malformed YAML recording files
- [ ] Add tests for Unicode/non-ASCII subprocess output
- [ ] Improve coverage of `plugin.py` (currently 51%, limited by pytest plugin import order)

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

- [ ] Tag and release v0.1.0
- [ ] Add security scanning to CI (bandit, safety)
- [ ] Add pre-commit hooks configuration
