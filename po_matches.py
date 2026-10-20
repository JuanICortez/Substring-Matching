import logging
import re
from collections.abc import Generator

from utils import Token, TokenTypes, create_parser, setup_logging

type Substitution = dict[str, list[int]]
type Relation = tuple[int, int]
type Preds = dict[int, frozenset[int]]

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


def get_available(preds: Preds, consumed: frozenset[int]) -> list[int]:
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
) -> Generator[Substitution, None, None]:

    if len(P) == P_idx:
        if len(preds) == len(consumed):
            yield subst
        return

    pattern = P[P_idx]
    avail = get_available(preds, consumed)

    match pattern.type:
        case TokenTypes.NUM:
            target = int(pattern.value)

            if target in avail:
                yield from dfs(P, P_idx + 1, preds, consumed | {target}, subst)

        case TokenTypes.VAR:
            var = pattern.value

            if var in subst:
                if subst[var] in avail:
                    yield from dfs(P, P_idx + 1, preds, consumed | {subst[var]}, subst)

                return

            for target in avail:
                yield from dfs(
                    P,
                    P_idx + 1,
                    preds,
                    consumed | {target},
                    {**subst, var: target},
                )

        case TokenTypes.ELLIPSIS:
            # Empty case
            yield from dfs(P, P_idx + 1, preds, consumed, subst)

            # Ellipsis consumes the available elements
            for target in avail:
                yield from dfs(P, P_idx, preds, consumed | {target}, subst)


def matching(pattern: list[Token], partial_order: list[int]) -> Substitution | None:
    substitution: Substitution = {}
    transitive_order = transitive_closure(partial_order)
    preds = build_preds(transitive_order)

    return dfs(pattern, 0, preds, frozenset(), substitution)


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
