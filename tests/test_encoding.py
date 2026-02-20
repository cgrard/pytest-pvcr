from pytest_pvcr.recordings import (
    Recording,
    _decode_value,
    _encode_value,
)


class TestEncodeValue:
    def test_str(self):
        assert _encode_value("hello") == "hello"

    def test_none(self):
        assert _encode_value(None) is None

    def test_bytes(self):
        result = _encode_value(b"hello")
        assert isinstance(result, dict)
        assert "__base64__" in result
        assert result["__base64__"] == "aGVsbG8="


class TestDecodeValue:
    def test_str(self):
        assert _decode_value("hello") == "hello"

    def test_none(self):
        assert _decode_value(None) is None

    def test_bytes(self):
        result = _decode_value({"__base64__": "aGVsbG8="})
        assert result == b"hello"

    def test_regular_dict(self):
        d = {"key": "value"}
        assert _decode_value(d) == d


class TestRoundtrip:
    def test_bytes_roundtrip(self):
        original = b"\x00\x01\x02\xff binary data"
        assert _decode_value(_encode_value(original)) == original

    def test_str_roundtrip(self):
        original = "hello world"
        assert _decode_value(_encode_value(original)) == original


class TestRecordingBytesEncoding:
    def test_to_encoded_dict_bytes(self):
        rec = Recording(
            ["cmd"],
            stdout=b"binary output",
            stderr=b"binary error",
            rc=0,
            duration=100,
        )
        d = rec.to_encoded_dict()
        assert isinstance(d["stdout"], dict)
        assert "__base64__" in d["stdout"]
        assert isinstance(d["stderr"], dict)
        assert "__base64__" in d["stderr"]

    def test_from_encoded_dict_bytes(self):
        d = {
            "args": ["cmd"],
            "stdout": {"__base64__": "aGVsbG8="},
            "stderr": {"__base64__": "ZXJy"},
            "rc": 0,
            "iteration": 1,
        }
        rec = Recording.from_encoded_dict(d)
        assert rec.stdout == b"hello"
        assert rec.stderr == b"err"

    def test_full_roundtrip_bytes(self):
        original = Recording(
            ["cmd"],
            stdin=b"input bytes",
            stdout=b"output bytes",
            stderr=b"error bytes",
            rc=0,
            duration=100,
            iteration=1,
        )
        d = original.to_encoded_dict()
        restored = Recording.from_encoded_dict(d)
        assert restored.stdin == original.stdin
        assert restored.stdout == original.stdout
        assert restored.stderr == original.stderr
