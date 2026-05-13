import copy
from typing import Any, Type, TypeVar
import typing
import pytest
import pandas as pd
from datetime import timedelta
import random
from bluebird_dt.core import Aircraft, Environment, WindField
from bluebird_dt.manager import EnvironmentManager
from bluebird_dt.simulator import Simulator
from deepdiff import DeepDiff
from bluebird_dt.events.event_dtypes import EventDtypes


T = TypeVar("T")

@pytest.fixture
def flight_plan() -> dict[str, Any]:
    return {
        "callsign": "CFC4406",
        "datetime": "2020-01-01 10:30:00",
        "start_datetime": None,
        "end_datetime": None,
        "squawk": "4035",
        "origin": "EGNT",
        "dest": "LFSN",
        "unexpanded_route":"EGNT Z5 LFSN",
        "route_filed": ['BOWNE'],
        "sector_crossing_seq": None,
        "actype": "C30J",
        "milcivil": "C",
        "requested_flight_level": 0,
        "filed_true_airspeed": None,
        "intention_code": "S",
        "ufid": "CFC4406",
        "assigned_squawk": "4035",
    }

def pick_random_next_sector(sectors: list[str], current_sector: str) -> str:
    """
    Helper function that picks a random next sector for coords, incomms etc.
    Returns "background" if no alternative sector exists (single-sector layout).
    """
    candidates = [s for s in sectors if s != current_sector]
    return random.choice(candidates) if candidates else "background"

def build_default_test_df(dataframe_schema: dict[str, str], env: Environment[Aircraft, WindField, WindField]) -> pd.DataFrame:
    default_row = {
        col: {} if dtype == "object" 
        else None
        for col, dtype in dataframe_schema.items()
    }
    df = pd.DataFrame([default_row])
    df["datetime"] = env.datetime
    df = df.set_index("datetime")
    return df

def build_test_df_for_multiple_ac(dataframe_schema: dict[str, str], env: Environment[Aircraft, WindField, WindField], props_to_set: list[tuple[str, any]], input_datetime: pd.Timestamp | None = None) -> pd.DataFrame:
    """
    Build a test dataframe for the given type to inject into classes with multiple rows for different callsigns
    Add a row for each callsign and set properties based on a dictionary input
    All other properties given a default
    """
    rows = []
    for callsign in env.aircraft.keys():
        row = {
            col: {} if dtype == "object" 
            else None
            for col, dtype in dataframe_schema.items()
        }
        for key, value in props_to_set:
            row[key] = value
        row["callsign"] = callsign
        if "ufid" in dataframe_schema:
            row["ufid"] = callsign
        rows.append(row)

    df = pd.DataFrame(rows)
    df["datetime"] = env.datetime if input_datetime is None else input_datetime
    df = df.set_index("datetime")
    return df

def build_coordination_test_df(env: Environment[Aircraft, WindField, WindField], props_to_set: list[tuple[str, typing.Any]], timedelta_to_test: int, dataframe_schema: dict[str, str]) -> pd.DataFrame:
    """
    Build a test dataframe for coordination type to inject into classes with multiple rows for different callsigns
    Coordination is slightly different from the others because we need to set from_sector using the current sector per aircraft
    Add a row for each callsign and set properties based on a dictionary input
    All other properties given a default
    """
    rows = []
    for callsign in env.aircraft.keys():
        existing_coords = env.coordinations.get(callsign)
        from_sector = existing_coords[0].from_sector if existing_coords else env.aircraft[callsign].current_sector
        row = {
            col: {} if dtype == "object" 
            else None
            for col, dtype in dataframe_schema.items()
        }
        for key, value in props_to_set:
            row[key] = value
        row["from_sector"] = from_sector
        row["callsign"] = callsign
        if "ufid" in dataframe_schema:
            row["ufid"] = callsign
        rows.append(row)

    df = pd.DataFrame(rows)
    df["datetime"] = env.datetime
    df = df.set_index("datetime")
    df.index = df.index + timedelta(seconds=timedelta_to_test)
    return df

def is_deeply_equal(a: Any, b: Any) -> bool:
    """
    Nicely named wrapper around DeepDiff comparison
    """
    return not DeepDiff(a, b)

def setup_test_sim() -> tuple[Environment[Aircraft, WindField, WindField], EnvironmentManager[Aircraft, WindField, WindField], Aircraft, str, pd.Timestamp, pd.Timestamp]:
    """
    Helper function to set up a sim and provide useful objects for tests
    Use this to avoid repeating this in every individual test
    """
    simulator = Simulator.from_category(category="Springfield", scenario_name="example-scenario")
    assert "SPRINGFIELD" in simulator.manager.environment.airspace.sectors
    manager = simulator.manager
    env = simulator.manager.environment
    callsign = list(env.aircraft.keys())[0]
    episode_start = env.datetime - timedelta(seconds=1)
    episode_end = env.datetime + timedelta(seconds=1)
    aircraft = env.aircraft[callsign]
    return (env, manager, aircraft, callsign, episode_start, episode_end)

def get_to_and_from_sectors(env: Environment[Aircraft, WindField, WindField], callsign: str) -> tuple[str, str]:
    sectors = [sector for sector in env.airspace.sectors]
    assert callsign in env.aircraft
    current_sector = env.aircraft[callsign].current_sector
    to_sector = pick_random_next_sector(sectors, current_sector)
    return [current_sector, to_sector]
