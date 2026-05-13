from copy import deepcopy

from shapely.affinity import rotate, translate
from shapely.geometry import Point, Polygon
from typing_extensions import override

from bluebird_dt.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Fixes, Route, Sector, Volume
from bluebird_dt.utility.geo_helper import GeoHelper


class TwoSectors(AirspaceGenerator):
    """
    Generates and airspace with two square sectors side by side
    """

    width: float
    height: float
    fl_limits: tuple[int, int]
    origin: tuple[float, float]

    def __init__(
        self,
        width: float,
        height: float,
        fl_limits: tuple[int, int],
        origin: tuple[float, float] = (0.0, 0.0),
    ):
        if width <= 0:
            raise ValueError("Width must be positive.")

        if height <= 0:
            raise ValueError("Height must be positive.")

        if (fl_limits[0] < 0) or (fl_limits[1] < 0):
            raise ValueError("Flight level limits must be positive.")

        if fl_limits[0] >= fl_limits[1]:
            raise ValueError("Maximum flight level must exceed minimum flight level.")

        if not (-180 <= origin[0] <= 180):
            raise ValueError("Longitude must be in the range [-180, 180]")

        if not (-90 <= origin[1] <= 90):
            raise ValueError("Latitude must be in the range [-90, 90]")

        self.width = width
        self.height = height
        self.fl_limits = fl_limits
        self.origin = origin

    @override
    def generate_airspace(self) -> tuple[Airspace, list[Route]]:
        geo_helper = GeoHelper(self.origin)
        polygon1 = Polygon(
            [
                (-0.5 * self.height, -0.5 * self.width),
                (0.5 * self.height, -0.5 * self.width),
                (0.5 * self.height, 0.5 * self.width),
                (-0.5 * self.height, 0.5 * self.width),
            ]
        )

        # Transpose both polygons to be centred around the origin
        polygon2 = deepcopy(polygon1)

        # Transpose both polygons so the origin is at their boundary
        polygon1 = translate(polygon1, yoff=self.width * 0.5)
        polygon2 = translate(polygon2, yoff=self.width * -0.5)

        sectors = {
            "sector_1": Sector([Volume.from_shapely_polygon(polygon1, self.fl_limits, geo_helper=geo_helper)]),
            "sector_2": Sector([Volume.from_shapely_polygon(polygon2, self.fl_limits, geo_helper=geo_helper)]),
        }

        alpha = 45
        rotation_origin = (0, 0)

        fixes_shapely_dict = {
            "ABYSS": Point(0, 0),
            "DEMON": rotate(Point(self.height * 0.25, 0), alpha, rotation_origin),
            "SANTA": rotate(Point(self.height * 0.35, 0), alpha, rotation_origin),
            "GATES": rotate(Point(self.height * 0.25, 0), -alpha, rotation_origin),
            "SIN": rotate(Point(self.height * 0.35, 0), -alpha, rotation_origin),
            "WITCH": rotate(Point(-self.height * 0.25, 0), alpha, rotation_origin),
            "SIREN": rotate(Point(-self.height * 0.35, 0), alpha, rotation_origin),
            "HAUNT": rotate(Point(-self.height * 0.25, 0), -alpha, rotation_origin),
            "LIMBO": rotate(Point(-self.height * 0.35, 0), -alpha, rotation_origin),
        }

        # now translate the points to the correct position using the inverse projection
        fixes = Fixes({name: geo_helper.inverse_projection((f.x, f.y)) for name, f in fixes_shapely_dict.items()})

        routes = [
            Route(["SIREN", "WITCH", "ABYSS", "DEMON", "SANTA"]),
            Route(["SIREN", "WITCH", "ABYSS", "GATES", "SIN"]),
            Route(["SIREN", "WITCH", "ABYSS", "HAUNT", "LIMBO"]),
            Route(["LIMBO", "HAUNT", "ABYSS", "GATES", "SIN"]),
            Route(["LIMBO", "HAUNT", "ABYSS", "DEMON", "SANTA"]),
            Route(["LIMBO", "HAUNT", "ABYSS", "WITCH", "SIREN"]),
            Route(["SIN", "GATES", "ABYSS", "HAUNT", "LIMBO"]),
            Route(["SIN", "GATES", "ABYSS", "DEMON", "SANTA"]),
            Route(["SIN", "GATES", "ABYSS", "WITCH", "SIREN"]),
            Route(["SANTA", "DEMON", "ABYSS", "WITCH", "SIREN"]),
            Route(["SANTA", "DEMON", "ABYSS", "GATES", "SIN"]),
            Route(["SANTA", "DEMON", "ABYSS", "HAUNT", "LIMBO"]),
        ]

        return Airspace(sectors, fixes), routes
