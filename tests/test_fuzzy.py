from pathlib import Path

from pytest_pvcr.recordings import FUZZY_PLACEHOLDER, Recordings


def _make_recordings(fuzzy_matchers: list[str]) -> Recordings:
    """Create a Recordings instance with fuzzy matchers for testing."""
    return Recordings(
        Path("/dev/null"),
        record_mode="none",
        fuzzy_matchers=fuzzy_matchers,
    )


class TestFuzzyCompiler:
    def test_no_matchers(self):
        recs = _make_recordings([])
        assert recs._fuzzy_compiler(["ls", "/tmp"]) == ["ls", "/tmp"]

    def test_simple_replacement(self):
        recs = _make_recordings(["--dry-run"])
        result = recs._fuzzy_compiler(["kubectl", "--dry-run", "apply"])
        assert result == [
            "kubectl",
            FUZZY_PLACEHOLDER,
            "apply",
        ]

    def test_group_matching(self):
        recs = _make_recordings([r"^.+\/(kubeconfig)$"])
        result = recs._fuzzy_compiler(["/home/user/kubeconfig"])
        assert result == [f"{FUZZY_PLACEHOLDER}kubeconfig"]

    def test_multiple_matchers(self):
        recs = _make_recordings(["--verbose", "--debug"])
        result = recs._fuzzy_compiler(["cmd", "--verbose", "--debug"])
        assert result == [
            "cmd",
            FUZZY_PLACEHOLDER,
            FUZZY_PLACEHOLDER,
        ]

    def test_no_match(self):
        recs = _make_recordings(["nonexistent"])
        result = recs._fuzzy_compiler(["ls", "/tmp"])
        assert result == ["ls", "/tmp"]

    def test_partial_replacement_in_arg(self):
        recs = _make_recordings(["/tmp/test"])
        result = recs._fuzzy_compiler(["cat", "/tmp/test/file.txt"])
        assert FUZZY_PLACEHOLDER in result[1]
        assert "file.txt" in result[1]
