import logging

from utils import Token, TokenTypes, create_parser, get_target, setup_logging

type Substitution = dict[str, list[int]]


logger = logging.getLogger(__name__)


def dfs(
    P: list[Token],
    P_idx: int,
    T: list[int],
    T_idx: int,
    subst: Substitution,
    seen: set[str],
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
                return dfs(P, P_idx + 1, T, T_idx + 1, subst.copy(), seen)

            return None

        case TokenTypes.VAR:
            if target is None:
                return None

            pattern_var = pattern.value
            next_target = T_idx + 1
            next_pattern = P_idx if next_target < len(T) else P_idx + 1

            # First time we see the variable
            if pattern_var not in subst:
                subst[pattern_var] = [target]
                return dfs(P, next_pattern, T, next_target, subst.copy(), seen)

            # Variable already in substitution

            if pattern_var in seen:
                # Matching with new instance of already seen variable
                matched_list = subst[pattern_var]
                matching_target = T_idx + len(matched_list)

                if matching_target > len(T):
                    return None

                if matched_list == T[T_idx:matching_target]:
                    return dfs(P, P_idx + 1, T, matching_target, subst.copy(), seen)

                return None

            # Still matching with first instance of variable
            subst[pattern_var].append(target)

            # Eagerly try to append as many elements as possible
            if (
                new_subst := dfs(P, next_pattern, T, next_target, subst.copy(), seen)
            ) is not None:
                return new_subst

            # Appended too many elements
            subst[pattern_var].pop()
            seen.add(pattern_var)

            return dfs(P, P_idx + 1, T, T_idx, subst.copy(), seen)

        case TokenTypes.ELLIPSIS:
            # Empty Case
            if (
                new_subst := dfs(P, P_idx + 1, T, T_idx, subst.copy(), seen)
            ) is not None:
                return new_subst

            # Ellipsis Matches One or More Elements
            return dfs(P, P_idx, T, T_idx + 1, subst.copy(), seen)


def matching(pattern: list[Token], target: list[int]) -> Substitution | None:
    substitution: Substitution = {}
    seen: set[str] = set()

    return dfs(pattern, 0, target, 0, substitution, seen)


def main() -> None:
    parser = create_parser("List DFS Matching")
    args = parser.parse_args()

    setup_logging(args.log_level)

    token_pattern: list[Token] = args.pattern
    res = matching(token_pattern, args.target)
    print("No Match" if res is None else f"{res = }")


if __name__ == "__main__":
    main()
