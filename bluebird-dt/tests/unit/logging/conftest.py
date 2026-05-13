import copy
import uuid
from typing import Any
import pytest
import pandas as pd
from datetime import datetime
import random

@pytest.fixture
def unique_log_name() -> str:
    """
    Create a unique log name for each test run.
    """
    return str(uuid.uuid4())


@pytest.fixture
def callsign_1() -> str:
    return "RYR33UY"


@pytest.fixture
def callsign_2() -> str:
    return "BAW123"


@pytest.fixture
def trajectory_1() -> list[list[float]]:
    return [[-1.3, 51.0], [-1.3, 50.9]]


@pytest.fixture
def trajectory_2() -> list[list[float]]:
    return [[-1.301, 51.01], [-1.31, 50.91]]


@pytest.fixture
def trajectory_3() -> list[list[float]]:
    return [[-1.302, 51.02], [-1.32, 50.92]]


@pytest.fixture
def windows_1() -> list[list[list[float]]]:
    return [
        [[-1.1, 51.1], [-1.3, 51.2]],
        [[-1.4, 50.6], [-1.6, 50.8]],
    ]


@pytest.fixture
def windows_2() -> list[list[list[float]]]:
    return [
        [[-1.101, 51.101], [-1.301, 51.201]],
        [[-1.401, 50.601], [-1.601, 50.801]],
    ]


@pytest.fixture
def windows_3() -> list[list[list[float]]]:
    return [
        [[-1.102, 51.102], [-1.302, 51.202]],
        [[-1.402, 50.602], [-1.602, 50.802]],
    ]


@pytest.fixture
def action_data_1(callsign_1: str) -> list[dict[str, Any]]:
    return [
        {
            "callsign": callsign_1,
            "time": 1561961400.0,
            "coordinates": [-1.3, 51.0],
            "action_type": "change_flight_level_to",
            "value": "300.0",
        },
        {
            "callsign": callsign_1,
            "time": 1561961412.0,
            "coordinates": [-1.3, 50.9],
            "action_type": "outcomm",
            "value": "",
        },
    ]


@pytest.fixture
def action_data_2(callsign_1: str) -> list[dict[str, Any]]:
    return [
        {
            "callsign": callsign_1,
            "time": 1561961406.0,
            "coordinates": [-1.301, 51.001],
            "action_type": "change_flight_level_to",
            "value": "310.0",
        },
        {
            "callsign": callsign_1,
            "time": 1561961418.0,
            "coordinates": [-1.301, 50.901],
            "action_type": "outcomm",
            "value": "",
        },
    ]


@pytest.fixture
def action_data_3(callsign_2: str) -> list[dict[str, Any]]:
    return [
        {
            "callsign": callsign_2,
            "time": 1561961412.0,
            "coordinates": [-1.302, 51.002],
            "action_type": "change_flight_level_to",
            "value": "310.0",
        },
        {
            "callsign": callsign_2,
            "time": 1561961424.0,
            "coordinates": [-1.302, 50.902],
            "action_type": "outcomm",
            "value": "",
        },
    ]

@pytest.fixture
def flight_plan() -> dict[str, Any]:
    return {
        "callsign": "CFC4406",
        "datetime": "2020-01-01 10:30:00",
        "start_datetime": None,
        "end_datetime": None,
        "squawk": 4035,
        "origin": "EGNT",
        "dest": "LFSN",
        "unexpanded_route":"EGNT Z5 LFSN",
        "route_filed": ['RHINO'],
        "sector_crossing_seq": None,
        "actype": "C30J",
        "milcivil": "C",
        "requested_flight_level": 0,
        "filed_true_airspeed": None,
        "intention_code": "S",
        "ufid": "CFC4406",
        "assigned_squawk": 4035,
    }

def extract_first_row_from_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function that pulls out the first row from a dataframe or returns False if not present
    """
    if df.empty: return [False, None]
    row = df.iloc[0]
    return [False, None] if row.empty else [True, row]

def query_row_from_df(callsign: str, theDatetime: datetime, df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper function that pulls out a row from a dataframe for given callsign and datetime or returns False if not present
    """
    if df.empty: return [False, None]
    results = df[(df["datetime"] == theDatetime) & (df["callsign"] == callsign)]
    if results.empty: return [False, None]
    row = results.iloc[0]
    return [False, None] if row.empty else [True, row]

def pick_random_next_sector(sectors: list, current_sector: list) -> list:
    """
    Helper function that picks a random next sector for coords, incomms etc.
    Returns "background" if no alternative sector exists (single-sector layout).
    """
    input_sectors = copy.deepcopy(sectors)
    if current_sector in input_sectors:
        input_sectors.remove(current_sector)
    return random.choice(input_sectors) if input_sectors else "background"
