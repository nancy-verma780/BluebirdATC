from shapely.affinity import rotate
from shapely.geometry import Point, Polygon
from typing_extensions import override

from bluebird_dt.airspace_generator.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Area, Fixes, Route, Sector
from bluebird_dt.core.airway import Airway
from bluebird_dt.utility.geo_helper import GeoHelper


class SectorI(AirspaceGenerator):
    """
    I-shaped sector Airspace generator.
    """

    def __init__(
        self,
        width: float,
        height: float,
        fl_limits: tuple[int, int],
        alpha: float = 0.0,
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
        alpha: float, default = 0
            The angle at which the I-shaped sector is rotated (-180 < alpha < 180).
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

        if not (-180 <= alpha <= 180):
            raise ValueError("Alpha must be in the range [-180, 180].")

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

        gh = GeoHelper(origin=self.origin)

        [min_fl, max_fl] = self.fl_limits

        i_polygon = rotate(
            Polygon(
                [
                    (-0.5 * self.height, -0.5 * self.width),
                    (0.5 * self.height, -0.5 * self.width),
                    (0.5 * self.height, 0.5 * self.width),
                    (-0.5 * self.height, 0.5 * self.width),
                ]
            ),
            angle=self.alpha,
            origin=self.origin,
        )

        # extract coordinates and transform to projected Pos2D points in degrees
        coords_pos2d = gh.inverse_projection(list(i_polygon.exterior.coords))

        sectors = {"sector_i": Sector([Volume(Area(coords_pos2d), min_fl, max_fl)])}

        # Note that tests rely on these being in the order: SPIRIT, AIR, WATER, EARTH, FIRE
        fixes_shapely_dict = {
            "SPIRIT": rotate(Point(self.height * 0.65, 0), angle=self.alpha, origin=self.origin),
            "AIR": rotate(Point(self.height * 0.5, 0), angle=self.alpha, origin=self.origin),
            "WATER": Point(0, 0),
            "EARTH": rotate(Point(-self.height * 0.5, 0), angle=self.alpha, origin=self.origin),
            "FIRE": rotate(Point(-self.height * 0.65, 0), angle=self.alpha, origin=self.origin),
        }

        # now translate the points to the correct position using the inverse projection
        fixes = Fixes({name: gh.inverse_projection((f.x, f.y)) for name, f in fixes_shapely_dict.items()})

        routes = [
            Route(["FIRE", "EARTH", "WATER", "AIR", "SPIRIT"]),
            Route(["SPIRIT", "AIR", "WATER", "EARTH", "FIRE"]),
        ]

        airways = {"UL1": Airway.from_list_of_fixes("UL1", routes[0].filed, 0, 660, fixes)}

        return Airspace(sectors, fixes, airways), routes
