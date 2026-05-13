import ast

import pandas as pd


def convert_string_to_lists(df: pd.DataFrame, col_names: list[str]) -> pd.DataFrame:
    """
    Convert lists represented as strings to list objects for specific columns

    Parameters
    ----------
    df: pandas.DataFrame
        A pandas DataFrame
    col_names:
        The columns in the dataframe for which lists as strings will be converted to lists

    Returns
    -------
    pandas.DataFrame
    """
    for col_name in col_names:
        df[col_name] = df[col_name].apply(ast.literal_eval)
    return df


def apply_sid_or_star(
    route_fixes: list[str], route_fix_types: list[str], df: pd.DataFrame, ELEM_TYPE: str
) -> tuple[list[str], list[str]]:
    """
    Add sid or star to route by expanding with a list of fixes to represent the sid or star.

    Parameters
    ----------
    route_fixes: list of str
        Original route as a list of fixes
    route_fix_types: list of str
        List of the type of each fix in route_fixes
    df: pandas.DataFrame
        ELEM dataframe containing the sid or star as a list of fixes
    ELEM_TYPE: str
        The type of ELEM_TYPE in the route_fix_types to be expanded

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple. The first element is the route after expanding the sids or start, the second element is the
        type of each fix in this expanded route.
    """
    # if there are any ELEM types, then we need to replace them with the SID route
    try:
        sid_idx = route_fix_types.index(ELEM_TYPE)
        sid_name = route_fixes[sid_idx]

        # get the ELEM route out of the ELEM dataframe
        sid_route = df.loc[df.name == sid_name].fixes.to_numpy()[0]

        # replace the ELEM with the route
        route_fixes = route_fixes[:sid_idx] + sid_route + route_fixes[sid_idx + 1 :]
        route_fix_types = route_fix_types[:sid_idx] + ["FIX" for _ in sid_route] + route_fix_types[sid_idx + 1 :]

    # a ValueError will be raised if there are no ELEM types in the route
    except ValueError:
        pass

    return route_fixes, route_fix_types


def find_first_fix(route: list[str], fix_list: list[str]) -> str | None:
    """
    Find the first fix on a route matching any of the elements in a given list.

    Parameters
    ----------
    route: list[str]
        A route, specified as a list of fix names.
    fix_list: list[str]
        A list of fixes which are to be matched

    Returns
    -------
    str or None
        The first fix in the route which matches one of the fixes in fix_list.
        None if no match.
    """
    for fix in route:
        if fix in fix_list:
            return fix
    return None
