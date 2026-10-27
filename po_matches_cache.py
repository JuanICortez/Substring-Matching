import logging
import re
from collections.abc import Generator

from utils import Token, TokenTypes, create_parser, setup_logging

type Substitution = dict[str, list[int]]
type Relation = tuple[int, int]
type Preds = dict[int, frozenset[int]]
type State = tuple[int, frozenset[int], frozenset[tuple[str, int]]]

logger = logging.getLogger(__name__)

END: int = -1


def parse_partial_order(input_str: str) -> list[tuple[int, int]]:
    matches = re.findall(r"\(([^)]+)\)", input_str)

    return [
        tuple(int(x) if x.strip().isdigit() else END for x in m.split(","))
        for m in matches
    ]


def transitive_closure(relations: list[Relation]) -> list[Relation]:
    closure = {rel for rel in relations}
    added = True

    while added:
        added = False
        new_relations = set()

        for a, b in closure:
            for c, d in closure:
                if b == c and (a, d) not in closure:
                    new_relations.add((a, d))
                    added = True

        closure.update(new_relations)

    return list(closure)


def build_preds(relations: list[Relation]) -> Preds:
    preds = {}

    for a, b in relations:
        preds.setdefault(a, set())

        if b == END:
            continue

        preds.setdefault(b, set())

        if a != b:
            preds[b].add(a)

    return {k: frozenset(v) for k, v in preds.items()}


def get_possible_matches(preds: Preds, consumed: frozenset[int]) -> list[int]:
    return [
        node
        for node, predecessors in preds.items()
        if predecessors.issubset(consumed) and node not in consumed
    ]


def dfs(
    P: list[Token],
    P_idx: int,
    preds: Preds,
    consumed: frozenset[int],  # Elements that were already matched with
    subst: Substitution,
    seen: set[State],
) -> Generator[Substitution, None, None]:

    state = (P_idx, consumed, frozenset(subst.items()))
    if state in seen:
        return
    seen.add(state)

    if len(P) == P_idx:
        if len(preds) == len(consumed):
            yield subst
        return

    pattern = P[P_idx]
    avail = get_possible_matches(preds, consumed)

    match pattern.type:
        case TokenTypes.NUM:
            target = int(pattern.value)

            if target in avail:
                yield from dfs(P, P_idx + 1, preds, consumed | {target}, subst, seen)

        case TokenTypes.VAR:
            var = pattern.value

            if var in subst:
                if subst[var] in avail:
                    yield from dfs(
                        P, P_idx + 1, preds, consumed | {subst[var]}, subst, seen
                    )

                return

            for target in avail:
                yield from dfs(
                    P,
                    P_idx + 1,
                    preds,
                    consumed | {target},
                    {**subst, var: target},
                    seen,
                )

        case TokenTypes.ELLIPSIS:
            # Empty case
            yield from dfs(P, P_idx + 1, preds, consumed, subst, seen)

            # Ellipsis consumes the available elements
            for target in avail:
                yield from dfs(P, P_idx, preds, consumed | {target}, subst, seen)


def matching(pattern: list[Token], partial_order: list[int]) -> Substitution | None:
    substitution: Substitution = {}
    transitive_order = transitive_closure(partial_order)
    preds = build_preds(transitive_order)

    return dfs(pattern, 0, preds, frozenset(), substitution, set())


def main() -> None:
    parser = create_parser("All Permutations of List DFS Matching", parse_partial_order)
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


# Elements in PO? -> Repeated elements
# Topological Order

# Que condiciones tiene el match -> Version Declarativa
# Que pasos hay que seguir para conseguir un match -> Version Algoritmica

# x++; x++;
# [(1, 1), (1, -)]

# printf();