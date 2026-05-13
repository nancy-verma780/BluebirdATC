from __future__ import annotations

import typing
from itertools import pairwise

from pydantic import BaseModel, ValidationError, field_validator, model_validator
from typing_extensions import override

from bluebird_dt.core.fixes import Fixes
from bluebird_dt.mixin import Comparison


class Route(BaseModel, Comparison):
    """
    Flight plan through named locations.
    """

    filed: list[str]
    current: list[str] | None = None

    @field_validator("filed")
    def validate_filed(cls, value: list[str]) -> list[str]:
        if len(value) < 1:
            raise ValueError("Filed route must contain at least one location name.")
        return value

    @model_validator(mode="after")
    def set_current_if_missing(self) -> Route:
        if self.current is None:
            self.current = self.filed
        return self

    def __init__(self, *args, **kwargs):  # noqa: ANN002, ANN003
        """
        Construct a new instance, can also accept non-keyword args.

        Parameters
        ----------
        filed: list[str]
            The filed route of the aircraft, as a list of fix names.
        current: list[str], optional
            The current route of the aircraft, as a list of fix names. If not provided, defaults to filed route.

        Examples
        --------
        >>> route = Route(["ALFA", "BRAVO", "CHAR", "DELTA"])
        >>> route = Route(["ALFA", "BRAVO", "CHAR", "DELTA"], ["BRAVO", "DELTA"])

        """
        if args and not kwargs:
            if len(args) < 1 or len(args) > 2:
                raise ValidationError("Route() takes one or two positional arguments: filed, current")
            kwargs = {"filed": args[0]} if len(args) == 1 else {"filed": args[0], "current": args[1]}
        super().__init__(**kwargs)

    @staticmethod
    def from_json(s: str) -> Route:
        """
        Construct a new instance from JSON representation.

        Parameters
        ----------
        s: str
            A string representation of the Route in a JSON/list structure.

        Returns
        ----------
        Route

        Examples
        --------
        >>> Route.from_json(
        >>>    '''
        >>>    {
        >>>        "filed": ["A", "B", "C", "D"],
        >>>        "current": ["C", "D"]
        >>>    }
        >>>    '''
        >>> )
        """
        return Route.model_validate_json(s)

    @staticmethod
    def load(filename: str) -> Route:
        """
        Construct a new instance from a file.

        Parameters
        ----------
        filename: str
            Path to a JSON file with a Route definition in a list format.

        Returns
        ----------
        Route
        """

        with open(filename) as fd:
            s = fd.read()

        return Route.from_json(s)

    def data(self) -> dict[str, list[str]]:
        """
        Get the current data as a serialisable list.

        Returns
        ----------
        Dictionary containing the filed and current routes.
        """

        return {"filed": self.filed, "current": self.current}

    def to_json(self) -> str:
        """
        Serialise the instance to JSON string.

        Returns
        ----------
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

        s = self.to_json()

        with open(filename, "w") as fd:
            fd.write(s)

    @override
    def __str__(self) -> str:
        """
        Create a human-readable representation of the filed and current route.
        If the route is, for example, "A", "B", "C", then the returned string will be "A>B>C".

        Returns
        ----------
        str
        """

        return f"Filed: {'>'.join(self.filed)} Current: {'>'.join(self.current)}"

    def segments(self) -> typing.Iterator[tuple[str, str]]:
        """
        Create an iterator of the filed Route segments (segment is
        composed of two consecutive location names).

        Returns
        ----------
        Iterator[tuple[str, str]]
            The Route segments.
        """

        return pairwise(self.filed)

    def length(self, fixes: Fixes) -> float:
        """
        Calculate the length [nmi] of the filed Route.

        Parameters
        ----------
        fixes: Fixes
            A dictionary of names and 2D locations on the globe.

        Returns
        ----------
        float
            The length [nmi] of the Route.
        """

        total = 0.0

        if len(self.filed) > 1:
            for a, b in self.segments():
                total += fixes.places[a].distance(fixes.places[b])

        return total

    def dists_to_end(self, fixes: Fixes) -> dict[str, float]:
        """
        For each Fix, return distance to end of filed Route (final Fix).

        Parameters
        ----------
        fixes: Fixes
            A dictionary of names and 2D locations.

        Returns
        ----------
        Dict[str, float]
            {Name of fix: distance to end of Route}
        """

        total_distance_so_far = 0.0
        route_distances = {}

        # start at final fix and loop backwards
        route_reverse = self.filed[::-1]
        route_distances[route_reverse[0]] = total_distance_so_far

        # compute distance between each consecutive pair of fixes (segments)
        # save the cumulative distance from final fix
        for end_fix, start_fix in pairwise(route_reverse):
            total_distance_so_far += fixes.places[end_fix].distance(fixes.places[start_fix])
            route_distances[start_fix] = total_distance_so_far

        return route_distances

    @staticmethod
    def add_origin_destination_to_filed_route(route_filed: list[str], origin: str, dest: str) -> list[str]:
        """
        Add origin and destination to start and end of filed route, if they are not already present.

        Parameters
        ----------
        route_filed: list of strings
            Original filed route
        origin: str
            Origin of flight
        dest: str
            Destination of flight

        Returns
        ----------
        list of strings
            New filed route, with origin and destination added at the start and end if required not already present
        """

        # only update the route if origin or destination is not None
        route_list = list(route_filed)
        route_is_empty = len(route_list) == 0

        if origin is not None and (route_is_empty or route_list[0] != origin):
            route_list.insert(0, origin)

        if dest is not None and (route_is_empty or route_list[-1] != dest):
            route_list.append(dest)

        return route_list
