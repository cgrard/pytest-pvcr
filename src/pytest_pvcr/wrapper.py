import logging
import subprocess
import sys
import time
from typing import TYPE_CHECKING, Any

logger = logging.getLogger("pvcr")

if TYPE_CHECKING:
    from .recordings import Recordings


class PVCRBlockedRunException(Exception): ...


def install_wrapper() -> None:
    sys.modules["subprocess"] = SubprocessWrapper


def uninstall_wrapper() -> None:
    sys.modules["subprocess"] = SubprocessWrapper.pvcr_orig_cls


def run(
    args: list[str] | str,
    *other_args: Any,
    stdin: bytes | str | None = None,
    **other_kwargs: Any,
) -> subprocess.CompletedProcess:
    recording = SubprocessWrapper.pvcr_history.append(args, stdin)

    # Return an existing instance if there is a recorded command
    if recording.saved:
        logger.debug("Replaying recorded command: %s", args)
        if SubprocessWrapper.pvcr_do_wait:
            time.sleep(recording.duration / 1000000)

        return SubprocessWrapper.pvcr_orig_cls.CompletedProcess(
            recording.args,
            returncode=recording.rc,
            stdout=recording.stdout,
            stderr=recording.stderr,
        )

    should_block = (
        SubprocessWrapper.pvcr_block_run
        or SubprocessWrapper.pvcr_history.block_unrecorded
    )
    if should_block:
        logger.warning("Blocked unrecorded command: %s", args)
        raise PVCRBlockedRunException(f"Blocked unrecorded command: {args}")

    # Really execute the command and record its result
    logger.debug("Executing and recording command: %s", args)
    before = time.time()
    if "stdout" not in other_kwargs and "stderr" not in other_kwargs:
        other_kwargs["capture_output"] = True
    else:
        other_kwargs.setdefault("stdout", SubprocessWrapper.pvcr_orig_cls.PIPE)
        other_kwargs.setdefault("stderr", SubprocessWrapper.pvcr_orig_cls.PIPE)
    ret = SubprocessWrapper.pvcr_orig_cls.run(
        args, *other_args, stdin=stdin, **other_kwargs
    )
    after = time.time()

    recording.stdout = ret.stdout
    recording.stderr = ret.stderr
    recording.rc = ret.returncode
    recording.duration = (after - before) * 1000000

    # Save the result to the recordings file
    SubprocessWrapper.pvcr_history.write(recording)

    return ret


class MetaSubprocessWrapper(type):
    """subprocess class wrapper metaclass."""

    pvcr_orig_cls = subprocess
    pvcr_current_request = None
    pvcr_do_wait: bool = True
    pvcr_record_mode: str = "none"
    pvcr_block_run: bool = False
    pvcr_history: Recordings
    pvcr_enabled: bool = False

    def __getattribute__(cls, item: str) -> Any:
        pvcr_orig_cls = object.__getattribute__(cls, "pvcr_orig_cls")
        pvcr_enabled = object.__getattribute__(cls, "pvcr_enabled")

        if pvcr_enabled and item == "run":
            return run

        if item == "pvcr_orig_cls":
            return pvcr_orig_cls

        try:
            return object.__getattribute__(cls, item)
        except AttributeError:
            return getattr(pvcr_orig_cls, item)


class SubprocessWrapper(metaclass=MetaSubprocessWrapper): ...
