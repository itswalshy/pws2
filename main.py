"""Entry point for the PowerWash Simulator cheat menu."""
from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass
from typing import Callable, Dict

from consts import CHEAT_NAMES, MENU_OPTIONS
from game_config import GameConfig, SUPPORTED_GAMES, get_game_config
from utility import AttachedProcess, ProcessNotFoundError, attach_to_process, log_address_chain

logger = logging.getLogger(__name__)


ToggleCallback = Callable[[AttachedProcess, GameConfig, bool], None]


@dataclass
class CheatFeature:
    """Represents an individual cheat toggle."""

    identifier: str
    label: str
    callback: ToggleCallback
    enabled: bool = False

    def toggle(self, process: AttachedProcess, config: GameConfig) -> None:
        self.enabled = not self.enabled
        logger.info("%s -> %s", self.label, "ON" if self.enabled else "OFF")
        self.callback(process, config, self.enabled)


class CheatManager:
    """Container class that keeps track of all registered cheat features."""

    def __init__(self, process: AttachedProcess, config: GameConfig) -> None:
        self.process = process
        self.config = config
        self.features: Dict[str, CheatFeature] = {}

    def register(self, identifier: str, callback: ToggleCallback) -> None:
        label = CHEAT_NAMES.get(identifier, identifier.title())
        self.features[identifier] = CheatFeature(identifier, label, callback)

    def toggle(self, identifier: str) -> None:
        feature = self.features.get(identifier)
        if not feature:
            logger.error("Unknown cheat '%s'", identifier)
            return
        feature.toggle(self.process, self.config)


# ---------------------------------------------------------------------------
# Cheat callback implementations
# ---------------------------------------------------------------------------

def toggle_infinite_soap(process: AttachedProcess, config: GameConfig, enabled: bool) -> None:
    """Enable or disable the Infinite Soap cheat.

    TODO: Write to ``config.base_addresses["soap"]`` once the actual pointer
    chain is known for both v1 and v2.  Use :func:`log_address_chain` during
    development to validate the addresses.
    """

    address = config.base_addresses["soap"]
    log_address_chain("soap", address)
    logger.debug(
        "(Infinite Soap) Would %s memory at %s for process %s",
        "freeze" if enabled else "release",
        address.describe(),
        process.pid,
    )


def toggle_instant_clean(process: AttachedProcess, config: GameConfig, enabled: bool) -> None:
    """Enable or disable the Instant Clean cheat.

    TODO: Implement the hook using ``config.function_hooks["instant_clean"]``.
    The legacy trainer likely used a code injection here; mirror that approach
    once updated offsets are available.
    """

    hook = config.function_hooks["instant_clean"]
    log_address_chain("instant_clean", hook)
    logger.debug(
        "(Instant Clean) Would %s hook at %s for process %s",
        "install" if enabled else "remove",
        hook.describe(),
        process.pid,
    )


def toggle_flight(process: AttachedProcess, config: GameConfig, enabled: bool) -> None:
    """Enable or disable the Flight cheat.

    TODO: Identify whether flight toggles rely on a boolean flag or velocity
    manipulation.  Once confirmed, update the write logic using
    ``config.base_addresses["flight"]``.
    """

    address = config.base_addresses["flight"]
    log_address_chain("flight", address)
    logger.debug(
        "(Flight) Would set flight flag to %s at %s for process %s",
        enabled,
        address.describe(),
        process.pid,
    )


def toggle_dirt_esp(process: AttachedProcess, config: GameConfig, enabled: bool) -> None:
    """Enable or disable the Dirt ESP cheat.

    TODO: Confirm whether this feature manipulates a function hook or simply
    extends a timer.  Replace the log statement with the actual memory writes.
    """

    hook = config.function_hooks["dirt_esp"]
    log_address_chain("dirt_esp", hook)
    logger.debug(
        "(Dirt ESP) Would %s visualization hook at %s for process %s",
        "enable" if enabled else "disable",
        hook.describe(),
        process.pid,
    )


# ---------------------------------------------------------------------------
# CLI helpers
# ---------------------------------------------------------------------------

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PowerWash Simulator Cheat Menu")
    parser.add_argument(
        "--game-version",
        "-g",
        default="v1",
        choices=sorted(SUPPORTED_GAMES.keys()),
        help="Target game version (default: v1)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase logging verbosity (can be specified multiple times)",
    )
    return parser.parse_args(argv)


def configure_logging(verbosity: int) -> None:
    level = logging.WARNING
    if verbosity == 1:
        level = logging.INFO
    elif verbosity >= 2:
        level = logging.DEBUG

    logging.basicConfig(level=level, format="[%(levelname)s] %(name)s: %(message)s")


def build_manager(config: GameConfig) -> CheatManager:
    process = attach_to_process(config)
    manager = CheatManager(process, config)
    manager.register("soap", toggle_infinite_soap)
    manager.register("instant_clean", toggle_instant_clean)
    manager.register("flight", toggle_flight)
    manager.register("dirt_esp", toggle_dirt_esp)
    return manager


def display_menu() -> None:
    print("\n=== Trippy's Deluxe Washer 2 ===")
    for key, description in MENU_OPTIONS.items():
        print(f"[{key}] {description}")


def run_menu(manager: CheatManager) -> None:
    while True:
        display_menu()
        choice = input("> ").strip().lower()
        if choice == "q":
            print("Exiting cheat menu. Happy washing!")
            break
        elif choice == "1":
            manager.toggle("soap")
        elif choice == "2":
            manager.toggle("instant_clean")
        elif choice == "3":
            manager.toggle("flight")
        elif choice == "4":
            manager.toggle("dirt_esp")
        else:
            print("Invalid option. Please try again.")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    configure_logging(args.verbose)

    game_version = args.game_version
    try:
        config = get_game_config(game_version)
    except KeyError as exc:
        logger.error(str(exc))
        return 1

    print(f"Selected target: {config.name} ({game_version})")

    try:
        manager = build_manager(config)
    except ProcessNotFoundError as exc:
        logger.error("%s", exc)
        print(
            "Unable to attach to the game process. Ensure the correct game version "
            "is running and try again."
        )
        return 1

    run_menu(manager)
    return 0


if __name__ == "__main__":
    sys.exit(main())
