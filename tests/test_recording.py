from pytest_pvcr.recordings import Recording


class TestRecordingInit:
    def test_defaults(self):
        rec = Recording(["ls", "/tmp"])
        assert rec.args == ["ls", "/tmp"]
        assert rec.stdin is None
        assert rec.stdout is None
        assert rec.stderr is None
        assert rec.rc is None
        assert rec.duration is None
        assert rec.iteration == 1
        assert rec.saved is False

    def test_all_fields(self):
        rec = Recording(
            ["echo", "hi"],
            stdin="input",
            stdout="hi\n",
            stderr="",
            rc=0,
            duration=1000,
            iteration=2,
            saved=True,
        )
        assert rec.stdout == "hi\n"
        assert rec.iteration == 2
        assert rec.saved is True


class TestToEncodedDict:
    def test_minimal(self):
        rec = Recording(["ls"], rc=0, duration=500)
        d = rec.to_encoded_dict()
        assert d["args"] == ["ls"]
        assert d["rc"] == 0
        assert d["duration"] == 500
        assert d["iteration"] == 1
        assert "stdin" not in d
        assert "stdout" not in d
        assert "stderr" not in d

    def test_full(self):
        rec = Recording(
            ["echo"],
            stdin="in",
            stdout="out",
            stderr="err",
            rc=0,
            duration=100,
        )
        d = rec.to_encoded_dict()
        assert d["stdin"] == "in"
        assert d["stdout"] == "out"
        assert d["stderr"] == "err"


class TestFromEncodedDict:
    def test_roundtrip(self):
        original = Recording(
            ["echo", "hello"],
            stdin="in",
            stdout="out",
            stderr="err",
            rc=0,
            duration=42,
            iteration=3,
        )
        d = original.to_encoded_dict()
        restored = Recording.from_encoded_dict(d)
        assert restored.args == original.args
        assert restored.stdin == original.stdin
        assert restored.stdout == original.stdout
        assert restored.stderr == original.stderr
        assert restored.rc == original.rc
        assert restored.duration == original.duration
        assert restored.iteration == original.iteration

    def test_missing_fields(self):
        rec = Recording.from_encoded_dict({})
        assert rec.args == []
        assert rec.rc is None
        assert rec.iteration == 1
        assert rec.stdin is None
        assert rec.stdout is None
        assert rec.stderr is None
        assert rec.duration is None


class TestCopy:
    def test_copy(self):
        src = Recording(
            ["ls"],
            stdin="in",
            stdout="out",
            stderr="err",
            rc=0,
            iteration=5,
            duration=999,
        )
        dst = Recording(["placeholder"])
        dst.copy(src)
        assert dst.args == ["ls"]
        assert dst.stdin == "in"
        assert dst.stdout == "out"
        assert dst.stderr == "err"
        assert dst.rc == 0
        assert dst.iteration == 5
        assert dst.duration == 999


class TestMatch:
    def test_args_only(self):
        rec = Recording(["ls", "/tmp"])
        assert rec.match(["ls", "/tmp"]) is True

    def test_args_no_match(self):
        rec = Recording(["ls", "/tmp"])
        assert rec.match(["ls", "/var"]) is False

    def test_with_stdin(self):
        rec = Recording(["cat"], stdin="hello")
        assert rec.match(["cat"], stdin="hello") is True
        assert rec.match(["cat"], stdin="other") is False
        assert rec.match(["cat"]) is False

    def test_with_iteration(self):
        rec = Recording(["ls"], iteration=2)
        assert rec.match(["ls"], iteration=2) is True
        assert rec.match(["ls"], iteration=1) is False
        assert rec.match(["ls"]) is True  # iteration=None ignores it


class TestEq:
    def test_equal(self):
        a = Recording(["ls"], stdin=None, iteration=1)
        b = Recording(["ls"], stdin=None, iteration=1)
        assert a == b

    def test_not_equal(self):
        a = Recording(["ls"], iteration=1)
        b = Recording(["ls"], iteration=2)
        assert a != b

    def test_non_recording(self):
        rec = Recording(["ls"])
        assert rec.__eq__("not a recording") is NotImplemented
