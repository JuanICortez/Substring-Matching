import logging

from utils import Token, TokenTypes, create_parser, setup_logging

type Substitution = dict[str, int]


logger = logging.getLogger(__name__)


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


def get_target(targets: list[int], target_idx: int) -> str | None:
    return targets[target_idx] if target_idx < len(targets) else None


def dfs(
    P: list[Token], P_idx: int, T: list[int], T_idx: int, subst: Substitution
) -> Substitution | None:

    logger.debug(f"Indexes: {P_idx = }, {T_idx = }")

    if P_idx == len(P):
        return subst if T_idx >= len(T) else None

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
                return dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())

            return None

        case TokenTypes.VAR:
            if target is None:
                return None

            pattern_var = pattern.value

            if pattern_var not in subst:
                subst[pattern_var] = target
                return dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())

            if subst[pattern_var] != target:
                return None

            return dfs(P, P_idx + 1, T, T_idx + 1, subst.copy())

        case TokenTypes.ELLIPSIS:
            # Empty Case
            if (new_subst := dfs(P, P_idx + 1, T, T_idx, subst.copy())) is not None:
                return new_subst

            # Ellipsis Matches One or More Elements
            return dfs(P, P_idx, T, T_idx + 1, subst.copy())


def matching(pattern: list[Token], target: list[int]) -> Substitution | None:
    substitution: Substitution = {}
    logger.debug(f"Lenghts: {len(pattern) = }, {len(target) = }\n")

    return dfs(pattern, 0, target, 0, substitution)


def main() -> None:
    parser = create_parser("Simple DFS Matching", parse_pattern)
    args = parser.parse_args()

    setup_logging(args.log_level)

    token_pattern: list[Token] = args.pattern
    res = matching(token_pattern, args.target)
    print("No Match" if res is None else f"{res = }")


if __name__ == "__main__":
    main()
