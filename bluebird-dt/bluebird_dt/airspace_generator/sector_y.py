from shapely.affinity import rotate, translate
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union
from typing_extensions import override

from bluebird_dt.airspace_generator.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Area, Fixes, Route, Sector
from bluebird_dt.utility.geo_helper import GeoHelper


class SectorY(AirspaceGenerator):
    """
    Sector Y scenario.
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
            The absolute degrees by which both branches are rotated from a vertical line (0 < alpha < 180).
            For example, alpha=90 results in a T shaped Sector.
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

        if not (0 < alpha < 180):
            raise ValueError("Alpha must be in the range (0, 180).")

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

        # combined 3 I shapes to create a Y shape
        # use an I shape of half length here, so Y sector scale matches that of I & X.
        i_polygon = Polygon(
            [
                (-0.5 * self.height / 2, -0.5 * self.width),
                (0.5 * self.height / 2, -0.5 * self.width),
                (0.5 * self.height / 2, 0.5 * self.width),
                (-0.5 * self.height / 2, 0.5 * self.width),
            ]
        )
        _, y_mid = i_polygon.centroid.coords[0]
        _, _, x_max, _ = i_polygon.bounds
        offset_polygon = unary_union(
            [
                i_polygon,
                rotate(i_polygon, 180 - self.alpha, origin=(x_max, y_mid)),
                rotate(i_polygon, 180 + self.alpha, origin=(x_max, y_mid)),
            ]
        )

        # shift the polygon so its centre is at the origin.
        y_polygon = translate(offset_polygon, xoff=-self.height / 4, yoff=0.0)

        # extract coordinates and transform to projected Pos2D points in degrees
        coords_pos2d = gh.inverse_projection(list(y_polygon.exterior.coords))

        sectors = {"sector_y": Sector([Volume(Area(coords_pos2d), min_fl, max_fl)])}

        # rotation should happen before translation
        rotation_origin = (0, 0)

        # Note that tests rely on the order of the fixes in the dictionary
        # We have: - left arm: TRI -> BISHP -> GHOST
        #          - right arm: TRI -> CANON -> GOD
        #          - bottom arm: TRI -> SON -> DECAN
        fixes_shapely_dict = {
            "GOD": rotate(Point(self.height * 0.65, 0), angle=self.alpha, origin=rotation_origin),
            "CANON": rotate(Point(self.height * 0.5, 0), angle=self.alpha, origin=rotation_origin),
            "GHOST": rotate(Point(self.height * 0.65, 0), angle=-self.alpha, origin=rotation_origin),
            "BISHP": rotate(Point(self.height * 0.5, 0), angle=-self.alpha, origin=rotation_origin),
            "TRI": Point(0, 0),
            "SON": Point(-self.height * 0.5, 0),
            "DECAN": Point(-self.height * 0.65, 0),
        }

        # now translate the points to the correct position using the inverse projection
        fixes = Fixes({name: gh.inverse_projection((f.x, f.y)) for name, f in fixes_shapely_dict.items()})

        routes = [
            Route(["GOD", "CANON", "TRI", "SON", "DECAN"]),
            Route(["DECAN", "SON", "TRI", "CANON", "GOD"]),
            Route(["GHOST", "BISHP", "TRI", "SON", "DECAN"]),
            Route(["DECAN", "SON", "TRI", "BISHP", "GHOST"]),
            Route(["GHOST", "BISHP", "TRI", "CANON", "GOD"]),
            Route(["GOD", "CANON", "TRI", "BISHP", "GHOST"]),
        ]

        return Airspace(sectors, fixes), routes
