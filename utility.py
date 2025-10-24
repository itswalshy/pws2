"""Utility helpers for interacting with the target PowerWash Simulator process.

This module only provides lightweight scaffolding so that the trainer can be
ported between different game versions.  Actual memory scanning or injection is
intentionally left out and will be integrated later.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from game_config import GameConfig, MemoryAddress

logger = logging.getLogger(__name__)


class ProcessNotFoundError(RuntimeError):
    """Raised when the target game process is not found."""


@dataclass
class AttachedProcess:
    """Represents a handle to the running game process.

    The implementation is intentionally minimal.  When a memory library is
    plugged in, replace the `handle` attribute with whatever object that
    library returns (for example, a pymem instance).
    """

    name: str
    pid: int
    handle: Optional[object] = None


try:  # pragma: no cover - psutil is optional in the execution environment
    import psutil
except ImportError:  # pragma: no cover - allow the trainer to run without psutil
    psutil = None


def find_process_by_name(process_name: str) -> psutil.Process:
    """Return the first running process matching ``process_name``.

    Raises ``ProcessNotFoundError`` if the process cannot be found or if the
    optional :mod:`psutil` dependency is unavailable.  When the dependency is
    missing we raise an actionable message so that users understand how to
    install it before re-running the trainer.
    """

    if psutil is None:
        raise ProcessNotFoundError(
            "psutil is not installed. Install it with 'pip install psutil' "
            "before attempting to attach to the game process."
        )

    for process in psutil.process_iter(["name"]):
        if process.info.get("name") == process_name:
            return process
    raise ProcessNotFoundError(
        f"Could not locate running process '{process_name}'. Make sure the game "
        "is running before enabling cheats."
    )


def attach_to_process(config: GameConfig) -> AttachedProcess:
    """Attach to the game process described by ``config``."""

    logger.debug("Attempting to attach to %s", config.process_name)
    process = find_process_by_name(config.process_name)
    logger.info("Attached to %s (pid=%s)", config.process_name, process.pid)
    return AttachedProcess(name=config.process_name, pid=process.pid, handle=None)


def log_address_chain(label: str, address: MemoryAddress) -> None:
    """Convenience helper that logs address chains for documentation purposes."""

    logger.debug("%s address chain: %s", label, address.describe())
