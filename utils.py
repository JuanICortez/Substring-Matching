import logging
import sys
from argparse import ArgumentParser
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


def parse_pattern(pattern: str) -> list[Token]:
    tokens: list[Token] = []

    for elem in pattern.split(","):
        if not (clean_elem := elem.strip()):
            continue

        match clean_elem:
            case _ if clean_elem.isidentifier():
                tokens.append(Token(TokenTypes.VAR, clean_elem))
            case _ if clean_elem.isnumeric():
                tokens.append(Token(TokenTypes.NUM, clean_elem))
            case "...":
                tokens.append(Token(TokenTypes.ELLIPSIS, clean_elem))
            case _:
                raise ValueError(f"Unrecognized token pattern: {clean_elem!r}")

    return tokens


def create_parser(
    prog_description: str,
) -> ArgumentParser:
    parser = ArgumentParser(prog=prog_description)

    parser.add_argument(
        "pattern", metavar="PATTERN", type=parse_pattern, help="Takes an input pattern"
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


def get_target(targets: list[int], target_idx: int) -> str | None:
    return targets[target_idx] if target_idx < len(targets) else None
