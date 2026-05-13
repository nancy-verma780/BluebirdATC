from __future__ import annotations

import json
from datetime import datetime
from functools import total_ordering
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, Field

from bluebird_dt.core.route import Route


def nan_to_none(s: str | float | None) -> str | None:
    """Convert various forms of nan into None"""
    if s is None or s == float("nan") or str(s).lower() in ("nan", "none"):
        return None
    return str(s)


def route_to_unexpanded_route(data: dict) -> str:
    """If unexpanded_route is unset, create it from the given route

    The origin and destination are removed:
    e.g., ["ORIG", "A", "B", "C", "DEST"] -> "A B C"
    """
    return " ".join(data["route"].filed[1:-1]).strip()


@total_ordering
class FlightPlan(BaseModel):
    """
    A static record of a flight plan, which contains entry and exit Coordination data for a Route, and an ordered
    list of sectors that the aircraft will pass through.
    """

    route: Route
    unexpanded_route: str = Field(default_factory=route_to_unexpanded_route)
    origin: str | None = Field(default=None)
    dest: str | None = Field(default=None)
    milcivil: Literal["M", "C"] | None = Field(default=None)
    sector_crossing_seq: str | None = Field(default=None)
    requested_flight_level: int | None = Field(default=None)
    filed_true_airspeed: int | None = Field(default=None)
    intention_code: Annotated[str | None, BeforeValidator(nan_to_none)] = Field(default=None)
    assigned_squawk: str | None = Field(default=None)
    start_datetime: datetime | None = Field(default=None)
    end_datetime: datetime | None = Field(default=None)

    def __init__(
        self,
        route: Route,
        **kwargs,  # noqa: ANN003 - handled by super().__init__
    ):
        """
        Construct a new instance.

        Parameters
        ----------
        route: Route
            The Route to be followed.
        unexpanded_route: optional str
            Route as described in original data flight plan. Airways have NOT been expanded to a list of fixes.
            If omitted, will be created automatically from route
        origin: string, optional
            4-letter ICAO code of origin airport
        dest: string, optional
            4-letter ICAO code of destination airport
        milcivil: string, optional
            Whether aircraft if civilian, 'C', or military, 'M'
        sector_crossing_seq: string, optional
            Sector Crossing Sequence. Planned sequence across sectors
        requested_flight_level: int, optional
            Preferred Cruising Flight Level as filed in Flight Plan
        filed_true_airspeed: int, optional
            Preferred Cruising Speed as filed in Flight Plan
        intention_code: str, optional
            String indicating where the aircraft intends to leave the UK FIR
        start_datetime: datetime, optional
            Datetime after which the flight plan is valid. If None then always valid.
        end_datetime: datetime, optional
            Datetime after which the flight plan is no longer valid. If None then always valid.
        """
        # Required for default-factory to trigger with unexpanded_route None
        # (is there a better way with field/model validators?)
        if "unexpanded_route" in kwargs and kwargs["unexpanded_route"] is None:
            del kwargs["unexpanded_route"]
        super().__init__(route=route, **kwargs)

    @staticmethod
    def from_json(s: str) -> FlightPlan | None:
        """
        Construct a new instance from string in JSON format.

        Parameters
        ----------
        s: str
            A string representation of a FlightPlan in JSON/dictionary format.

        Returns
        --------
        FlightPlan
        """

        if not s or json.loads(s) is None:
            return None

        return FlightPlan.model_validate_json(s)

    @staticmethod
    def load(filename: str) -> FlightPlan | None:
        """
        Construct a new instance from a file.

        Parameters
        ----------
        filename: str
            Path to a JSON file with a FlightPlan definition in a dictionary format.

        Returns
        --------
        FlightPlan
        """

        with open(filename) as fd:
            return FlightPlan.from_json(fd.read())

    def data(self) -> dict:
        """
        Create a dictionary with key/value pairs representing the FlightPlan data.

        Returns
        --------
        dict
        """

        return self.model_dump(mode="json")

    def to_json(self) -> str:
        """
        Serialise the instance to JSON string.

        Returns
        --------
        str
        """
        return self.model_dump_json(indent=4)

    def save(self, filename: str):
        """
        Write the instance to a file.

        Parameters
        ----------
        filename: str
            Path to file.
        """

        with open(filename, "w") as fd:
            fd.write(self.to_json())

    def __lt__(self, other: FlightPlan) -> bool:
        """Comparison of serialised FlightPlan"""
        return str(self.model_dump()) < str(other.model_dump())
