from lists_dfs import matching, parse_pattern


class TestMatching:
    def test_literal_match(self):
        assert matching(parse_pattern("1, 2, 3"), [1, 2, 3]) == {}

    def test_literal_mismatch(self):
        assert matching(parse_pattern("1, 2, 3"), [1, 2, 4]) is None

    def test_single_variable_grabs_remaining_elements(self):
        assert matching(parse_pattern("x"), [1, 2, 3]) == {"x": [1, 2, 3]}

    def test_repeated_variable_matches_equal_sublists(self):
        assert matching(parse_pattern("x, x"), [2, 2]) == {"x": [2]}

    def test_repeated_variable_rejects_unequal_sublists(self):
        assert matching(parse_pattern("x, x"), [2, 3]) is None

    def test_distinct_variables_each_bind_their_own_list(self):
        assert matching(parse_pattern("x, y, x"), [1, 2, 1]) == {
            "x": [1],
            "y": [2],
        }

    def test_variable_surrounded_by_literals(self):
        assert matching(parse_pattern("1, x, 2"), [1, 9, 2]) == {"x": [9]}

    def test_not_enough_elements_fails(self):
        assert matching(parse_pattern("x, y"), [1]) is None

    def test_ellipsis_matches_empty_pattern_and_target(self):
        assert matching(parse_pattern("..."), []) == {}

    def test_ellipsis_with_trailing_variable_requires_an_element(self):
        assert matching(parse_pattern("x, ..., y"), [1]) is None
        assert matching(parse_pattern("x, ..., y"), [1, 2, 3]) is not None
