from shapely.affinity import rotate
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from typing_extensions import override

from bluebird_dt.airspace_generator.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Area, Fixes, Route, Sector
from bluebird_dt.utility.geo_helper import GeoHelper


class SectorX(AirspaceGenerator):
    """
    Sector X scenario.
    """

    def __init__(
        self,
        width: float,
        height: float,
        fl_limits: tuple[int, int],
        alpha: float,
        origin: tuple[float, float] = (0.0, 0.0),
    ):
        """
        Construct a new instance.

        Parameters
        ----------
        width: float, NMI
            The width of the airways.
        height: float, NMI
           The height of the Airspace.
        fl_limits: list[float]
            The [min, max] flight level limits allowed in the Sector.
        alpha: float
            The absolute degrees by which both branches are rotated from a vertical line (0 < alpha < 90).
            For example, alpha=45 results in an X shape with 90 degrees between all branches.
        origin: (float, float), default = (0.0, 0.0)
            The longitude and latitude (in that order) which the sector is centred on
        """

        if width <= 0:
            raise ValueError("Width must be positive.")

        if height <= 0:
            raise ValueError("Height must be positive.")

        if (fl_limits[0] < 0) or (fl_limits[1] < 0):
            raise ValueError("Flight level limits must be positive.")

        if fl_limits[0] >= fl_limits[1]:
            raise ValueError("Maximum flight level must exceed minimum flight level.")

        if not (0 < alpha < 90):
            raise ValueError("Alpha must be in the range (0, 90).")

        if not (-180 <= origin[0] <= 180):
            raise ValueError("Longitude must be in the range [-180, 180]")

        if not (-90 <= origin[1] <= 90):
            raise ValueError("Latitude must be in the range [-90, 90]")

        self.width = width
        self.height = height
        self.fl_limits = fl_limits
        self.alpha = alpha
        self.origin = origin

    @override
    def generate_airspace(self) -> tuple[Airspace, list[Route]]:
        """
        Generate an airspace.

        Returns
        ----------
        Tuple[Airspace, list[Route]]
            A tuple with (Airspace, list of Routes).
        """

        # Lazy import for circular import issue
        from bluebird_dt.core import Volume

        gh = GeoHelper(self.origin)

        [min_fl, max_fl] = self.fl_limits

        # combine two, intersecting I shapes to create X shape
        i_polygon = Polygon(
            [
                (-0.5 * self.height, -0.5 * self.width),
                (0.5 * self.height, -0.5 * self.width),
                (0.5 * self.height, 0.5 * self.width),
                (-0.5 * self.height, 0.5 * self.width),
            ]
        )
        x_polygon = unary_union([rotate(i_polygon, -self.alpha), rotate(i_polygon, self.alpha)])

        # extract coordinates and transform to projected Pos2D points in degrees
        coords_pos2d = gh.inverse_projection(list(x_polygon.exterior.coords))

        sectors = {"sector_x": Sector([Volume(Area(coords_pos2d), min_fl, max_fl)])}

        # rotation should happen before translation
        rotation_origin = (0, 0)

        # Note that tests rely on the order of the fixes in the dictionary
        # We have: - upper-left arm: ABYSS -> GATES -> SIN
        #          - upper-right arm: ABYSS -> DEMON -> SANTA
        #          - lower-left arm: ABYSS -> HAUNT -> LIMBO
        fixes_shapely_dict = {
            "ABYSS": Point(0, 0),
            "DEMON": rotate(Point(self.height * 0.5, 0), self.alpha, rotation_origin),
            "SANTA": rotate(Point(self.height * 0.65, 0), self.alpha, rotation_origin),
            "GATES": rotate(Point(self.height * 0.5, 0), -self.alpha, rotation_origin),
            "SIN": rotate(Point(self.height * 0.65, 0), -self.alpha, rotation_origin),
            "WITCH": rotate(Point(-self.height * 0.5, 0), self.alpha, rotation_origin),
            "SIREN": rotate(Point(-self.height * 0.65, 0), self.alpha, rotation_origin),
            "HAUNT": rotate(Point(-self.height * 0.5, 0), -self.alpha, rotation_origin),
            "LIMBO": rotate(Point(-self.height * 0.65, 0), -self.alpha, rotation_origin),
        }

        # now translate the points to the correct position using the inverse projection
        fixes = Fixes({name: gh.inverse_projection((f.x, f.y)) for name, f in fixes_shapely_dict.items()})

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
