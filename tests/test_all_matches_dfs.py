import copy

from all_matches_dfs import matching, parse_pattern


def _run(pattern: str, target: list[int]) -> list[dict]:
    return [copy.deepcopy(subst) for subst in matching(parse_pattern(pattern), target)]

class TestMatching:
    def test_literal_match_yields_single_empty_substitution(self):
        assert _run("1, 2, 3", [1, 2, 3]) == [{}]

    def test_literal_mismatch_yields_nothing(self):
        assert _run("1, 2, 3", [1, 2, 4]) == []

    def test_repeated_variable_yields_single_consistent_match(self):
        assert _run("x, x", [2, 2]) == [{"x": [2]}]

    def test_repeated_variable_rejects_unequal_sublists(self):
        assert _run("x, x", [2, 3]) == []

    def test_bare_ellipsis_yields_single_empty_substitution(self):
        assert _run("...", [1, 2]) == [{}]

    def test_each_yielded_substitution_is_independent(self):
        results = _run("x, ...", [1, 2, 3])
        assert results == [{"x": [1, 2, 3]}, {"x": [1, 2]}, {"x": [1]}]
