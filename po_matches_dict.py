import logging
import re
from argparse import ArgumentTypeError
from collections.abc import Generator
from types import MappingProxyType

from utils import Token, TokenTypes, create_parser, setup_logging

type LineId = int
type EgraphId = str
type Variable = str

type Substitution = dict[Variable, tuple[EgraphId, LineId]]
type IdsMap = MappingProxyType[LineId, EgraphId]
type Relation = tuple[LineId, LineId]

type Preds = dict[LineId, frozenset[LineId]]
type State = tuple[LineId, frozenset[LineId], frozenset[tuple[Variable, tuple[EgraphId, LineId]]]]

logger = logging.getLogger(__name__)

END: int = -1


def parse_partial_order(input_str: str) -> list[tuple[int, int]]:
    matches = re.findall(r"\(([^)]+)\)", input_str)

    return [
        tuple(int(x) if x.strip().isdigit() else END for x in m.split(","))
        for m in matches
    ]


def parse_ids_map(input_str: str) -> IdsMap:
    """Parses 'id=value' pairs separated by ';' into an ids map."""
    ids_map = {}

    for pair in input_str.split(";"):
        if not pair.strip():
            continue

        node, sep, value = pair.partition(":")
        if not sep or not node.strip().isdigit():
            raise ArgumentTypeError(f"Invalid ids map entry: {pair.strip()!r}")

        ids_map[int(node)] = value.strip()

    return MappingProxyType(ids_map)


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
    ids_map: IdsMap,
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
        case TokenTypes.VALUE:
            for target in avail:
                if ids_map[target] == pattern.value:
                    yield from dfs(
                        P, P_idx + 1, ids_map, preds, consumed | {target}, subst, seen
                    )

        case TokenTypes.VAR if pattern.value in subst:
            for target in avail:
                if subst[pattern.value][0] == ids_map[target]:
                    yield from dfs(
                        P,
                        P_idx + 1,
                        ids_map,
                        preds,
                        consumed | {target},
                        subst,
                        seen,
                    )

        case TokenTypes.VAR:
            for target in avail:
                yield from dfs(
                    P,
                    P_idx + 1,
                    ids_map,
                    preds,
                    consumed | {target},
                    {**subst, pattern.value: (ids_map[target], target)},
                    seen,
                )

        case TokenTypes.ELLIPSIS:
            # Empty case
            yield from dfs(P, P_idx + 1, ids_map, preds, consumed, subst, seen)

            # Ellipsis consumes the available elements
            for target in avail:
                yield from dfs(
                    P, P_idx, ids_map, preds, consumed | {target}, subst, seen
                )


def matching(
    pattern: list[Token], partial_order: list[Relation], ids_map: IdsMap
) -> Generator[Substitution, None, None]:
    substitution: Substitution = {}
    transitive_order = transitive_closure(partial_order)
    preds = build_preds(transitive_order)

    return dfs(pattern, 0, ids_map, preds, frozenset(), substitution, set())


def main() -> None:
    parser = create_parser("All Permutations of List DFS Matching", parse_partial_order)
    parser.add_argument(
        "--map",
        metavar="IDS_MAP",
        type=parse_ids_map,
        required=True,
        help="Node values as 'id=value' pairs separated by ';' (e.g. '1:x++;2:x++')",
    )
    args = parser.parse_args()

    setup_logging(args.log_level)

    for match in matching(args.pattern, args.target, args.map):
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
