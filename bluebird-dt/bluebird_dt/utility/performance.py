import functools
import json

from bluebird_dt.utility.paths import (
    AIRCRAFT_WEIGHT_MAPPING_FILE,
    SIMPLE_PERFORMANCE_PROFILE_FILE,
    SIMPLE_PERFORMANCE_UNCERTAINTY_FILE,
)


@functools.cache
def get_performance_table(
    path: str | None,
) -> dict[str, dict[str, list[float]]]:
    """
    Load calibrated airspeed, rate of climb or descend and associated uncertainty tables
    for all aircraft

    Parameters
    ----------
    path: str
        Path to speed table data

    Return
    ------
    Dict:
        Dictionary containing speed profile data
    """
    if path is None:
        path = SIMPLE_PERFORMANCE_PROFILE_FILE

    try:
        with open(path) as aircraft_speed_profile:
            return json.load(aircraft_speed_profile)["aircraft"]

    except FileNotFoundError as e:
        raise FileNotFoundError("Speed profile data file could not be found!") from e


@functools.cache
def get_performance_uncertainty_table(
    path: str | None,
) -> dict[str, dict[str, dict[str, float]]]:
    """
    Load speed uncertainty tables for all aircraft

    Parameters
    ----------
    path: str
        Path to speed table data

    Return
    ------
    Dict:
        Dictionary containing speed uncertainty data
    """
    if path is None:
        path = SIMPLE_PERFORMANCE_UNCERTAINTY_FILE

    try:
        with open(path) as aircraft_speed_uncertainty:
            return json.load(aircraft_speed_uncertainty)["aircraft"]

    except FileNotFoundError as e:
        raise FileNotFoundError("Speed uncertainty data file could not be found!") from e


@functools.cache
def get_aircraft_key_mapping(path: str | None = None) -> dict[str, str]:
    """
    Load aircraft synonym type data. If no path supplied, fall back to a default aircraft weight mapping
    that matches the fallback simple performance and uncertainty files.

    The synonym file will be a 1:1 mapping of the ~1800 ICAO aircraft codes and the
    fallback file is a simplified version which maps aircraft types to weight categories (and in some cases
    weight categories to weight categories).

    Parameters
    ----------
    path: str
        Path to file that maps aircraft type to a lookup key for performance data.

    Return
    ------
    Dict:
        Dictionary containing aircraft type mapping
    """
    if path is None:
        path = AIRCRAFT_WEIGHT_MAPPING_FILE
    try:
        with open(path) as synonym_database:
            return json.load(synonym_database)

    except FileNotFoundError as e:
        raise FileNotFoundError("Aircraft synonym data file could not be found!") from e
