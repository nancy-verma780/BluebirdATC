import pandas as pd
import pytest

from bluebird_dt.utility.scenario_utils import (
    apply_sid_or_star,
    convert_string_to_lists,
    find_first_fix
)


class TestConvertStringToLists:
    """
    Test convert_string_to_lists
    """
    def test_convert_string_to_lists_converts_specified_columns_only(self):
        df = pd.DataFrame(
            {
                "a": ["[1, 2, 3]", "[4]"],
                "b": ["['X', 'Y']", "[]"],
                "c": ["not a list", "still not a list"],
            }
        )

        out = convert_string_to_lists(df, ["a", "b"])

        assert out is df
        assert out.loc[0, "a"] == [1, 2, 3]
        assert out.loc[1, "a"] == [4]
        assert out.loc[0, "b"] == ["X", "Y"]
        assert out.loc[1, "b"] == []
        assert out.loc[0, "c"] == "not a list"


    def test_convert_string_to_lists_handles_empty_col_names_no_change(self):
        df = pd.DataFrame({"a": ["[1]"], "b": ["[]"]})
        out = convert_string_to_lists(df, [])
        assert out is df
        assert out.loc[0, "a"] == "[1]"
        assert out.loc[0, "b"] == "[]"


    @pytest.mark.parametrize(
        "bad_value",
        [
            "not a python literal",
            "[1, 2, ",
            "{'a': 1",
        ],
    )
    def test_convert_string_to_lists_raises_on_invalid_literal(self,bad_value: str):
        df = pd.DataFrame({"a": [bad_value]})
        # ast.literal_eval typically raises (ValueError, SyntaxError)
        with pytest.raises((ValueError, SyntaxError)):
            convert_string_to_lists(df, ["a"])


class TestApplySidOrStar:
    """
    Test applying a SID or STAR
    """
    def test_apply_sid_or_star_expands_first_matching_elem_type(self):
        route_fixes = ["EGLL", "SID1", "FIX_AFTER"]
        route_fix_types = ["APT", "SID", "FIX"]

        df = pd.DataFrame(
            {
                "name": ["SID1"],
                "fixes": [["DCT1", "DCT2", "DCT3"]],
            }
        )

        new_fixes, new_types = apply_sid_or_star(route_fixes, route_fix_types, df, ELEM_TYPE="SID")

        assert new_fixes == ["EGLL", "DCT1", "DCT2", "DCT3", "FIX_AFTER"]
        assert new_types == ["APT", "FIX", "FIX", "FIX", "FIX"]


    def test_apply_sid_or_star_no_matching_elem_type_returns_unchanged(self):
        route_fixes = ["EGLL", "FIX1", "FIX2"]
        route_fix_types = ["APT", "FIX", "FIX"]
        df = pd.DataFrame({"name": ["SID1"], "fixes": [["A", "B"]]})

        new_fixes, new_types = apply_sid_or_star(route_fixes, route_fix_types, df, ELEM_TYPE="SID")

        assert new_fixes == route_fixes
        assert new_types == route_fix_types


    def test_apply_sid_or_star_only_expands_first_occurrence_of_elem_type(self):
        # Two SIDs appear; function expands only the first one due to .index(...)
        route_fixes = ["EGLL", "SID1", "SID2", "FIX_AFTER"]
        route_fix_types = ["APT", "SID", "SID", "FIX"]

        df = pd.DataFrame(
            {
                "name": ["SID1", "SID2"],
                "fixes": [["A", "B"], ["X", "Y"]],
            }
        )

        new_fixes, new_types = apply_sid_or_star(route_fixes, route_fix_types, df, ELEM_TYPE="SID")

        # Only SID1 expanded; SID2 remains (still of type "SID")
        assert new_fixes == ["EGLL", "A", "B", "SID2", "FIX_AFTER"]
        assert new_types == ["APT", "FIX", "FIX", "SID", "FIX"]


    def test_apply_sid_or_star_raises_if_elem_name_not_found_in_df(self):
        route_fixes = ["EGLL", "SID_MISSING", "FIX_AFTER"]
        route_fix_types = ["APT", "SID", "FIX"]

        df = pd.DataFrame(
        {
            "name": ["SID1"],
            "fixes": [["A", "B"]],
        }
        )

        # df.loc[df.name == sid_name].fixes.to_numpy()[0] => IndexError when no matching row
        with pytest.raises(IndexError):
            apply_sid_or_star(route_fixes, route_fix_types, df, ELEM_TYPE="SID")


@pytest.mark.parametrize(
    "route, fix_list, expected",
    [
        (["A", "B", "C"], ["X", "B"], "B"),
        (["A", "B", "C"], ["C", "B"], "B"),
        (["A", "B", "C"], ["X", "Y"], None),
        ([], ["A"], None), 
        (["A"], [], None),
    ],
)
def test_find_first_fix(route: list[str], fix_list: list[str], expected: str | None):
    """
    Test find_first_fix returns expected result for various input
    """
    assert find_first_fix(route, fix_list) == expected
