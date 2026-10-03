import logging
from collections.abc import Generator

from utils import Token, TokenTypes, create_parser, setup_logging

type Substitution = dict[str, list[int]]


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


def get_target(targets: list[str], target_idx: int) -> str | None:
    return targets[target_idx] if target_idx < len(targets) else None


def dfs(
    P: list[Token],
    P_idx: int,
    T: list[int],
    T_idx: int,
    subst: Substitution,
    seen: set[str],
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
            # Does not generate new match branches
            if int(pattern.value) == target:
                yield from dfs(P, P_idx + 1, T, T_idx + 1, subst.copy(), seen)

            return None

        case TokenTypes.VAR:
            if target is None:
                return None

            pattern_var = pattern.value
            next_target = T_idx + 1
            next_pattern = P_idx if next_target < len(T) else P_idx + 1

            # Obligatory match, does not generate new match branches
            if pattern_var not in subst:
                subst[pattern_var] = [target]
                yield from dfs(P, next_pattern, T, next_target, subst.copy(), seen)
                return

            # Validation match, does not generate new match branches
            if pattern_var in seen:
                matched_list = subst[pattern_var]
                matching_target = T_idx + len(matched_list)

                if matching_target > len(T):
                    return None

                if matched_list == T[T_idx:matching_target]:
                    yield from dfs(P, P_idx + 1, T, matching_target, subst.copy(), seen)

                return None

            # New match branch, generates new match branches
            subst[pattern_var].append(target)

            if (
                new_subst := dfs(P, next_pattern, T, next_target, subst.copy(), seen)
            ) is not None:
                yield from new_subst

            subst[pattern_var].pop()
            seen.add(pattern_var)

            yield from dfs(P, P_idx + 1, T, T_idx, subst.copy(), seen)

            seen.remove(pattern_var)

        case TokenTypes.ELLIPSIS:
            # Generates new match branches, can match zero elements
            if (
                new_subst := dfs(P, P_idx + 1, T, T_idx, subst.copy(), seen)
            ) is not None:
                yield from new_subst

            # Generates new match branches, can match more elements
            if (
                new_subst := dfs(P, P_idx, T, T_idx + 1, subst.copy(), seen)
            ) is not None:
                yield from new_subst

            


def matching(pattern: list[Token], target: list[int]) -> Substitution | None:
    substitution: Substitution = {}
    seen: set[str] = set()

    return dfs(pattern, 0, target, 0, substitution, seen)


def main() -> None:
    parser = create_parser("All Permutations of List DFS Matching", parse_pattern)
    args = parser.parse_args()

    setup_logging(args.log_level)

    res = matching(args.pattern, args.target)

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
