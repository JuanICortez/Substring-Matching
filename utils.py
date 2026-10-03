import logging
import sys
from argparse import ArgumentParser
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, auto


class TokenTypes(Enum):
    VAR = auto()
    NUM = auto()
    ELLIPSIS = auto()


@dataclass(slots=True, frozen=True)
class Token:
    type: TokenTypes
    value: str


def parse_cli_list(input_list: str) -> list[int]:
    list_values = filter(lambda s: s.isdigit(), list(input_list))
    return [int(item.strip()) for item in list_values]


def create_parser(
    prog_description: str,
    pattern_parser: Callable[[str], Token],
) -> ArgumentParser:
    parser = ArgumentParser(prog=prog_description)

    parser.add_argument(
        "pattern", metavar="PATTERN", type=pattern_parser, help="Takes an input pattern"
    )

    parser.add_argument(
        "--target",
        metavar="TARGET",
        type=parse_cli_list,
        help="List of intergers over which the pattern will be run",
    )

    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO"],
        help="Set logging level (default: INFO)",
    )

    return parser


def setup_logging(level: str) -> None:
    """
    Set up the logging configuration.

    Args:
        level: Minimum log level as a string (e.g., "DEBUG", "INFO").
    """
    logging_level = getattr(logging, level.upper(), logging.INFO)

    logging.basicConfig(
        level=logging_level,
        format="%(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
