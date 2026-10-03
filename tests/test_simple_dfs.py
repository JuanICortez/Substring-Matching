from simple_dfs import matching, parse_pattern


class TestMatching:
    def test_literal_match(self):
        assert matching(parse_pattern("1, 2, 3"), [1, 2, 3]) == {}

    def test_literal_mismatch(self):
        assert matching(parse_pattern("1, 2, 3"), [1, 2, 4]) is None

    def test_length_mismatch(self):
        assert matching(parse_pattern("1, 2"), [1, 2, 3]) is None

    def test_variable_binding(self):
        assert matching(parse_pattern("x, y"), [1, 2]) == {"x": 1, "y": 2}

    def test_repeated_variable_must_match_same_value(self):
        assert matching(parse_pattern("x, y, x"), [1, 2, 1]) == {"x": 1, "y": 2}

    def test_repeated_variable_conflict_fails(self):
        assert matching(parse_pattern("x, y, x"), [1, 2, 3]) is None

    def test_ellipsis_matches_zero_elements(self):
        assert matching(parse_pattern("1, ..."), [1]) == {}

    def test_ellipsis_matches_many_elements(self):
        assert matching(parse_pattern("1, ..."), [1, 2, 3, 4]) == {}

    def test_ellipsis_binds_surrounding_variables(self):
        assert matching(parse_pattern("1, x, ..."), [1, 9, 2, 3]) == {"x": 9}

    def test_bare_ellipsis_matches_anything(self):
        assert matching(parse_pattern("..."), []) == {}
        assert matching(parse_pattern("..."), [1, 2, 3]) == {}

    def test_ellipsis_does_not_swallow_trailing_pattern(self):
        assert matching(parse_pattern("x, ..., y"), [1]) is None
        assert matching(parse_pattern("x, ..., y"), [1, 2, 3]) == {"x": 1, "y": 3}
