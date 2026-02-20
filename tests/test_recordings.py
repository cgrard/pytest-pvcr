from pathlib import Path

from yaml import dump

try:
    from yaml import CDumper as Dumper
except ImportError:
    from yaml import Dumper

from pytest_pvcr.recordings import Recordings


def _make_recordings(
    tmp_path: Path,
    mode: str = "new",
    filename: str = "test.yaml",
    fuzzy_matchers: list[str] | None = None,
) -> Recordings:
    return Recordings(
        tmp_path / filename,
        record_mode=mode,
        fuzzy_matchers=fuzzy_matchers,
    )


def _write_yaml(path: Path, recordings: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write(dump({"recordings": recordings}, Dumper=Dumper))


class TestAppend:
    def test_new_recording(self, tmp_path):
        recs = _make_recordings(tmp_path)
        rec = recs.append(["ls", "/tmp"])
        assert rec.args == ["ls", "/tmp"]
        assert rec.saved is False
        assert rec.iteration == 1

    def test_iteration_increment(self, tmp_path):
        recs = _make_recordings(tmp_path)
        rec1 = recs.append(["ls"])
        rec2 = recs.append(["ls"])
        rec3 = recs.append(["echo", "hi"])
        assert rec1.iteration == 1
        assert rec2.iteration == 2
        assert rec3.iteration == 1

    def test_loads_existing(self, tmp_path):
        path = tmp_path / "test.yaml"
        _write_yaml(
            path,
            [
                {
                    "args": ["ls"],
                    "stdin": None,
                    "stdout": "file1\n",
                    "stderr": "",
                    "rc": 0,
                    "duration": 1000,
                    "iteration": 1,
                }
            ],
        )
        recs = _make_recordings(tmp_path)
        rec = recs.append(["ls"])
        assert rec.saved is True
        assert rec.stdout == "file1\n"
        assert rec.rc == 0


class TestWriteAndLoad:
    def test_write_and_reload(self, tmp_path):
        recs = _make_recordings(tmp_path)
        rec = recs.append(["echo", "hello"])
        rec.stdout = "hello\n"
        rec.stderr = ""
        rec.rc = 0
        rec.duration = 500
        recs.write(rec)
        assert rec.saved is True

        # Reload in a fresh Recordings instance
        recs2 = _make_recordings(tmp_path)
        rec2 = recs2.append(["echo", "hello"])
        assert rec2.saved is True
        assert rec2.stdout == "hello\n"
        assert rec2.rc == 0

    def test_creates_directory(self, tmp_path):
        recs = Recordings(
            tmp_path / "sub" / "dir" / "test.yaml",
            record_mode="new",
        )
        rec = recs.append(["ls"])
        rec.rc = 0
        rec.duration = 100
        recs.write(rec)
        assert (tmp_path / "sub" / "dir" / "test.yaml").exists()


class TestWriteModes:
    def test_mode_none(self, tmp_path):
        recs = _make_recordings(tmp_path, mode="none")
        rec = recs.append(["ls"])
        rec.rc = 0
        rec.duration = 100
        recs.write(rec)
        assert not (tmp_path / "test.yaml").exists()

    def test_mode_all_replaces(self, tmp_path):
        path = tmp_path / "test.yaml"
        _write_yaml(
            path,
            [
                {
                    "args": ["ls"],
                    "rc": 0,
                    "duration": 100,
                    "iteration": 1,
                },
                {
                    "args": ["echo"],
                    "rc": 0,
                    "duration": 200,
                    "iteration": 1,
                },
            ],
        )
        recs = _make_recordings(tmp_path, mode="all")
        rec = recs.append(["ls"])
        rec.rc = 42
        rec.duration = 999
        recs.write(rec)

        # Verify echo recording is still there
        recs2 = _make_recordings(tmp_path, mode="new")
        rec_echo = recs2.append(["echo"])
        assert rec_echo.saved is True
        assert rec_echo.rc == 0

    def test_mode_once_first_run(self, tmp_path):
        recs = _make_recordings(tmp_path, mode="once")
        rec = recs.append(["ls"])
        rec.rc = 0
        rec.duration = 100
        recs.write(rec)
        assert (tmp_path / "test.yaml").exists()

    def test_mode_once_subsequent(self, tmp_path):
        path = tmp_path / "test.yaml"
        _write_yaml(path, [])
        # File exists before Recordings is created
        recs = _make_recordings(tmp_path, mode="once")
        rec = recs.append(["new_cmd"])
        rec.rc = 0
        rec.duration = 100
        recs.write(rec)
        # Should not have written new_cmd
        recs2 = _make_recordings(tmp_path, mode="new")
        rec2 = recs2.append(["new_cmd"])
        assert rec2.saved is False


class TestBlockUnrecorded:
    def test_once_with_existing_file(self, tmp_path):
        path = tmp_path / "test.yaml"
        _write_yaml(path, [])
        recs = _make_recordings(tmp_path, mode="once")
        assert recs.block_unrecorded is True

    def test_once_without_file(self, tmp_path):
        recs = _make_recordings(tmp_path, mode="once")
        assert recs.block_unrecorded is False

    def test_new_mode(self, tmp_path):
        recs = _make_recordings(tmp_path, mode="new")
        assert recs.block_unrecorded is False

    def test_none_mode(self, tmp_path):
        recs = _make_recordings(tmp_path, mode="none")
        assert recs.block_unrecorded is False


class TestClean:
    def test_clean_history(self, tmp_path):
        recs = _make_recordings(tmp_path)
        recs.append(["ls"])
        recs.append(["echo"])
        assert len(recs._history) == 2
        recs.clean()
        assert len(recs._history) == 0

    def test_clean_with_write(self, tmp_path):
        path = tmp_path / "test.yaml"
        recs = _make_recordings(tmp_path)
        rec = recs.append(["ls"])
        rec.rc = 0
        rec.duration = 100
        recs.write(rec)
        assert path.exists()

        recs.clean(write=True)
        assert len(recs._history) == 0
        # File should exist but with empty recordings
        recs2 = _make_recordings(tmp_path)
        rec2 = recs2.append(["ls"])
        assert rec2.saved is False
