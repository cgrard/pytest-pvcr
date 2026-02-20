# pytest-pvcr

A pytest plugin that records and replays commands executed with `subprocess.run()`.

This plugin was inspired by VCR.py.

## Installation

This project can be installed via pip:

```
pip install pytest-pvcr
```

## Usage

```python
import subprocess
import pytest

@pytest.mark.pvcr()
def test_command():
    # subprocess.run is patched at runtime
    ret = subprocess.run(["ls", "/tmp"])

    assert rc.returncode == 0

@pytest.mark.pvcr(wait=False)
def test_command():
    # Super long command but since wait == False, PVCR does not wait its completion
    ret = subprocess.run(["sleep", "1000"])

    assert rc.returncode == 0
```

Run your tests:

```shell
pytest --pvcr-record-mode=new test_commands.py
```

### Record modes

There is three record modes:

```shell
# Only record new commands not previously recorded
pytest --pvcr-record-mode=new test_commands.py

# Record nothing
pytest --pvcr-record-mode=none test_commands.py

# Record all commands, even previously recorded ones
pytest --pvcr-record-mode=all test_commands.py
```

### Block execution

The execution of processes can be completely blocked.
This is useful to protect test environments from destructive commands.

```shell
pytest --pvcr-block-run test_commands.py
```

The test will fail if an unrecorded command is executed.

### Fuzzy matching

Commands can be fuzzy matched by defining one or more regex.

If a fuzzy regex has matching groups, the matched parts are kept for matching the commands.

If a fuzzy regex has no matching groups, the whole matched string is ignored when matching the commands.

```shell
# Ignore `--dry-run` arguments when matching commands
pytest --pvcr-fuzzy-matcher='--dry-run' test_commands.py

# Ignore the beginning of a path and keep the filename
pytest --pvcr-fuzzy-matcher='^.+\/(kubeconfig)$' test_commands.py
```

It's possible to automatically ignore the parent path of the test script.
This parameter is useful to make test assets portable.

```shell
pytest --pvcr-auto-fuzzy-match test_commands.py
```

## Python support

This plugin supports python >= 3.12

## Authors

* Fabien Dupont <fabien.dupont@eurofiber.com>
