import logging
import re

from utils import create_parser, setup_logging

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

def parse(tuples):
    occ = lambda e: e if isinstance(e, tuple) else (e, 0)   # v  ==  (v, 0)
    label, preds, succs = {}, {}, {}

    def add(n):
        label[n] = n[0]
        preds.setdefault(n, set())
        succs.setdefault(n, set())

    for a, b in tuples:
        a = occ(a); add(a)
        if b == END:
            continue
        b = occ(b); add(b)
        if a == b:                      # same occurrence, true self-loop
            continue
        preds[b].add(a)
        succs[a].add(b)
    return label, preds, {n: frozenset(s) for n, s in succs.items()}

def match(pattern, label, preds, succs):
    nodes = frozenset(label)
    seen, results = set(), set()

    def candidates(placed):             # one representative per (label, succs)
        reps = {}
        for n in nodes - placed:
            if preds[n] <= placed:
                reps.setdefault((label[n], succs[n]), n)
        return list(reps.values())

    def dfs(i, placed, env):
        key = (i, placed, frozenset(env.items()))
        if key in seen:
            return
        seen.add(key)
        if i == len(pattern):
            if placed == nodes:
                results.add(frozenset(env.items()))
            return
        tok = pattern[i]
        if tok == "...":
            dfs(i + 1, placed, env)
            for n in candidates(placed):
                dfs(i, placed | {n}, env)
            return
        for n in candidates(placed):
            l = label[n]
            if isinstance(tok, int):
                if l == tok:
                    dfs(i + 1, placed | {n}, env)
            elif env.get(tok, l) == l:
                dfs(i + 1, placed | {n}, {**env, tok: l})

    dfs(0, frozenset(), {})
    return [dict(r) for r in results]


def main() -> None:
    parser = create_parser("All Permutations of List DFS Matching", parse_partial_order)
    args = parser.parse_args()

    setup_logging(args.log_level)

    tc = transitive_closure(args.target)

    print("--" * 50)
    print(f"{tc = }")
    print("--" * 50)

    label, preds, succ = parse(tc)

    print()
    print(f"{label = }")
    print("--" * 50)
    print(f"{preds = }")
    print("--" * 50)
    print(f"{succ = } ")
    print()

    matches = match(args.pattern, label, preds, succ)

    print(f"{matches = }")

if __name__ == "__main__":
    main()


# Elements in PO? -> Repeated elements
# Topological Order

# Que condiciones tiene el match -> Version Declarativa
# Que pasos hay que seguir para conseguir un match -> Version Algoritmica


# x += 1; x += 2;

#  {1: a, 2: b, 3: a}
#  x++; printf(x); x++;
#  a-1    b-2      a-3
# (1,2), (2,3), (3,-) -> Se le calcula Transitive Closure

# {1: a, 2: b, 3: c}
# x = 1; x = 2; x = 3;
#  a-1    b-2    c-3
# (1,2), (2,3), (3,-)

# 1, 