"""Configuration definitions for supported PowerWash Simulator games.

This module centralizes all process names, base addresses, offsets, and
function hooks used by the cheat features.  Having a single source of truth
makes it easier to port the trainer between multiple game versions and keeps
memory-manipulation logic separate from the feature implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MemoryAddress:
    """Simple container describing a static memory address and optional offsets."""

    base: int
    offsets: List[int] = field(default_factory=list)

    def describe(self) -> str:
        """Return a human-readable description of the address chain."""

        formatted_offsets = " -> ".join(f"0x{offset:08X}" for offset in self.offsets)
        return f"0x{self.base:08X}" + (f" -> {formatted_offsets}" if formatted_offsets else "")


@dataclass(frozen=True)
class GameConfig:
    """Encapsulates memory configuration for a specific game build."""

    name: str
    process_name: str
    description: str
    base_addresses: Dict[str, MemoryAddress]
    function_hooks: Dict[str, MemoryAddress]
    notes: Optional[str] = None


# Known offsets for PowerWash Simulator (v1).  These values were gathered from
# the original release of the cheat menu and are kept for backwards compatibility.
PWS_V1_CONFIG = GameConfig(
    name="PowerWash Simulator",
    process_name="PowerWashSimulator.exe",
    description="Original release of PowerWash Simulator on Windows",
    base_addresses={
        # TODO: Document original offsets in more detail once verified.
        "currency": MemoryAddress(base=0x00000000, offsets=[]),
        "soap": MemoryAddress(base=0x00000000, offsets=[]),
        "dirt_level": MemoryAddress(base=0x00000000, offsets=[]),
        "flight": MemoryAddress(base=0x00000000, offsets=[]),
    },
    function_hooks={
        "instant_clean": MemoryAddress(base=0x00000000, offsets=[]),
        "dirt_esp": MemoryAddress(base=0x00000000, offsets=[]),
    },
    notes="Placeholder values copied from the legacy trainer. Replace with the\n"
    " actual addresses when porting the old functionality.",
)


# PowerWash Simulator 2 currently requires updated offsets.  These placeholders
# and TODO markers highlight where the new information should be inserted as
# soon as it becomes available from reverse-engineering or memory scanning.
PWS_V2_CONFIG = GameConfig(
    name="PowerWash Simulator 2",
    process_name="PowerWashSimulator2.exe",
    description="Sequel release. All offsets below must be verified.",
    base_addresses={
        # TODO: Identify the new base pointer for player currency/money.
        "currency": MemoryAddress(base=0x00000000, offsets=[]),
        # TODO: Locate the consumable soap quantity structure.
        "soap": MemoryAddress(base=0x00000000, offsets=[]),
        # TODO: Determine the address chain that stores the current dirt level.
        "dirt_level": MemoryAddress(base=0x00000000, offsets=[]),
        # TODO: Figure out how flight toggles are handled in PowerWash Simulator 2.
        "flight": MemoryAddress(base=0x00000000, offsets=[]),
    },
    function_hooks={
        # TODO: Update with the Instant Clean function hook once discovered.
        "instant_clean": MemoryAddress(base=0x00000000, offsets=[]),
        # TODO: Update with the Dirt ESP function hook once discovered.
        "dirt_esp": MemoryAddress(base=0x00000000, offsets=[]),
    },
    notes=(
        "All addresses are placeholders. Replace them after scanning the sequel's\n"
        " memory. Use MemoryAddress.describe() to log chains during development."
    ),
)


SUPPORTED_GAMES: Dict[str, GameConfig] = {
    "v1": PWS_V1_CONFIG,
    "v2": PWS_V2_CONFIG,
}


def get_game_config(version: str) -> GameConfig:
    """Return the configuration for the requested game version.

    Parameters
    ----------
    version:
        Short identifier for the desired game configuration ("v1", "v2", ...).

    Raises
    ------
    KeyError
        If the supplied version is not recognized.
    """

    normalized = version.lower()
    try:
        return SUPPORTED_GAMES[normalized]
    except KeyError as exc:  # pragma: no cover - defensive programming
        raise KeyError(f"Unsupported game version '{version}'.") from exc
