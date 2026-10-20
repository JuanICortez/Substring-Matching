import logging
from collections.abc import Generator

from utils import Token, TokenTypes, create_parser, get_target, setup_logging

type Substitution = dict[str, int]

logger = logging.getLogger(__name__)


def dfs(
    P: list[Token], P_idx: int, T: list[int], T_idx: int, subst: Substitution
) -> Generator[Substitution, None, None]:

    logger.debug(f"Indexes: {P_idx = }, {T_idx = }")

    if P_idx == len(P):
        if T_idx >= len(T):
            yield subst
        return

    if T_idx > len(T):
        return None

    pattern = P[P_idx]
    target = get_target(T, T_idx)

    logger.debug(f"Value: {P[P_idx].value = }")
    logger.debug(f"Target = {target}")
    logger.debug(f"Substitutions: {subst = }\n")

    match pattern.type:
        case TokenTypes.NUM:
            if int(pattern.value) == target:
                yield from dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())

            return None

        case TokenTypes.VAR:
            if target is None:
                return None

            pattern_var = pattern.value

            if pattern_var not in subst:
                subst[pattern_var] = target
                yield from dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())
                return

            if subst[pattern_var] != target:
                return None

            yield from dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())

        case TokenTypes.ELLIPSIS:
            # Empty Case
            if (new_subst := dfs(P, P_idx + 1, T, T_idx, subst.copy())) is not None:
                yield from new_subst

            # Ellipsis Matches One or More Elements
            yield from dfs(P, P_idx, T, T_idx + 1, subst.copy())


def matching(
    pattern: list[Token], target: list[int]
) -> Generator[Substitution, None, None]:
    substitution: Substitution = {}
    logger.debug(f"Lenghts: {len(pattern) = }, {len(target) = }\n")

    return dfs(pattern, 0, target, 0, substitution)


def main() -> None:
    parser = create_parser("Simple DFS Matching")
    args = parser.parse_args()

    setup_logging(args.log_level)

    token_pattern: list[Token] = args.pattern
    res = matching(token_pattern, args.target)

    for match in res:
        match_len = len(match)
        print("{", end=" ")
        for idx, (var, values) in enumerate(match.items()):
            if idx == match_len - 1:
                print(f"{var} -> {values}", end=" ")
            else:
                print(f"{var} -> {values}", end=", ")
        print("}")


if __name__ == "__main__":
    main()
