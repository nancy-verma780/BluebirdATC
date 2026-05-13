import math

import numpy as np
from shapely.geometry import MultiPolygon, Polygon
from typing_extensions import override

from bluebird_dt.airspace_generator.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Area, Fixes, Pos2D, Route, Sector, Volume


class SectorXPlus(AirspaceGenerator):
    """
    X-Plus shaped sector airspace generator.

    Creates an asymmetric cross-shaped sector with arms of varying lengths extending from a central hub. The sector
    has four arms extending in different directions with a central hub for traffic convergence. The East and North
    arms are connected by a diagonal segment that cuts across the corner, instead of a right-angle corner, creating
    a more complex boundary. The South arm is rotated at a specified angle from the vertical axis. Navigation fixes
    are positioned along each arm with both primary fixes at arm endpoints and offset terminal fixes beyond the
    sector boundary.

    The X-Plus shape consists of:
    - Four arms of different lengths: East (L2), North (L3), West (L1) and South (L4)
    - Between the East and North arms, a diagonal segment cuts across the corner, creating a 3-sided boundary
    - South arm rotated at a specified angle from the vertical axis
    - Central hub area (EGL) for traffic convergence and route distribution
    - Terminal fixes positioned outside the sector boundary for approach/departure routes

    Note: The coordinate system has L3 pointing north by default (rotation_deg=0), with the entire
    sector rotated by the specified rotation_deg parameter.
    """

    def __init__(
        self,
        origin: tuple[float, float] = (0.0, 0.0),
        fl_limits: tuple[int, int] = (200, 400),
        rotation_deg: float = -45.0,
        half_width_nmi: float = 10.0,
        L1: float = 3,
        L2: float = 6,
        L3: float = 5,
        L4: float = 4.5,
        W: float = 1,
        D: float = 2.5,
        F: float = 0.5,
        southern_leg_rotation_deg: float = 30.0,
        max_turn_angle_deg: float = 90.0,
    ):
        """
        Initialize the X-Plus sector generator.

        Parameters
        ----------
        origin : tuple[float, float], default=(0.0, 0.0)
            (longitude, latitude) of the sector center in degrees
        fl_limits : tuple[int, int], default=(200, 400)
            (minimum, maximum) flight levels for the sector
        rotation_deg : float, default=-45.0
            Rotation angle in degrees for the entire sector. 0 degrees faces L3 north, -90 degrees faces L2 north, etc.
        half_width_nmi : float, default=10.0
            Half-width scaling factor in nautical miles that scales the entire sector
        L1 : float, default=3
            Length of the West arm from center to boundary
        L2 : float, default=6
            Length of the East arm from center to boundary
        L3 : float, default=5
            Length of the North arm from center to boundary
        L4 : float, default=4.5
            Length of the South arm from center to boundary
        W : float, default=1
            Half-width of each arm creating the cross structure
        D : float, default=2.5
            Length of diagonal corner segments between East and North arms
        F : float, default=0.5
            Offset distance for terminal fixes beyond sector boundary
        southern_leg_rotation_deg : float, default=30.0
            Rotation angle in degrees for the southern leg from the vertical axis
        max_turn_angle_deg : float, default=90.0
            Maximum allowed turn angle in degrees for route validation

        Notes
        -----
        All dimensional parameters (L1, L2, L3, L4, W, D, F) are in relative units.

        The scaling works as: relative_units * half_width_nmi = nautical_miles. For example, with default
        half_width_nmi=10, L1=3 creates a 30 NMI arm length with arm width of 2 * 10 = 20 NMI (since W=1 by default).
        Uses the approximation that 1 degree latitude = 60 nautical miles for coordinate conversion.

        Raises
        ------
        ValueError
            If any parameter is invalid or out of expected range
        """
        # validate input parameters
        if not (-180 <= origin[0] <= 180):
            raise ValueError("Longitude must be in the range [-180, 180]")

        if not (-90 <= origin[1] <= 90):
            raise ValueError("Latitude must be in the range [-90, 90]")

        if fl_limits[0] < 0 or fl_limits[1] < 0:
            raise ValueError("Flight level limits must be positive")

        if fl_limits[0] >= fl_limits[1]:
            raise ValueError("Maximum flight level must exceed minimum flight level")

        if half_width_nmi <= 0:
            raise ValueError("Half-width must be positive")

        if any(param <= 0 for param in [L1, L2, L3, L4, W, D, F]):
            raise ValueError("All dimensional parameters (L1, L2, L3, L4, W, D, F) must be positive")

        if not (0 <= max_turn_angle_deg <= 180):
            raise ValueError("Maximum turn angle must be in the range [0, 180]")

        self.origin_lon, self.origin_lat = origin
        self.fl_limits = fl_limits
        self.rotation_deg = rotation_deg
        self.half_width_nmi = half_width_nmi
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.L4 = L4
        self.F = F
        self.W = W
        self.D = D
        self.southern_leg_rotation_deg = southern_leg_rotation_deg
        self.max_turn_angle_deg = max_turn_angle_deg

    @override
    def generate_airspace(self) -> tuple[Airspace, list[Route]]:
        """
        Generate the X-Plus shaped airspace with navigation fixes and routes.

        Creates an asymmetric cross-shaped sector with stepped diagonal boundaries and a rotated southern leg,
        positioned and scaled according to the initialization parameters. The sector includes 11 strategically
        placed navigation fixes and a comprehensive route network connecting terminal fixes through the central hub.

        Returns
        -------
        tuple[Airspace, list[Route]]
            A tuple containing:
            - Airspace: Complete airspace object with sectors and navigation fixes
            - list[Route]: List of routes providing full connectivity between terminal fixes (filtered by turn angle)

        Notes
        -----
        The generated airspace includes:
        - One sector named "sector_xplus" with the asymmetric cross boundary and rotated southern leg
        - 11 navigation fixes:
          * EGL: Central hub fix
          * QUAIL/SWIFT: East arm fixes
          * GOOSE/PEL: North arm fixes
          * CRANE/HERON: West arm fixes
          * FINCH/ROBIN: South arm fixes (rotated)
          * ALB/MACAW: Corner transition fixes for alternative routing between PEL and SWIFT
        - Up to 14 routes connecting the 4 terminal fixes (ROBIN, HERON, PEL, SWIFT), filtered by turn angle constraints
        """

        # construct the main body polygon with the diagonal cut
        main_body_coords = [
            (-self.L1, -self.W),
            (-self.L1, self.W),
            (-self.W, self.W),
            (-self.W, self.L3),
            (self.W, self.L3),
            (self.W, self.D),
            (self.D, self.W),
            (self.L2, self.W),
            (self.L2, -self.W),
            (self.W, -self.W),
            (-self.W, -self.W),
        ]
        main_body_poly = Polygon(main_body_coords)

        # define the southern leg centred on the EGL-FINCH line
        rotation_rad = math.radians(self.southern_leg_rotation_deg)
        s = math.sin(rotation_rad)
        c = math.cos(rotation_rad)

        finch_x = self.L4 * s
        finch_y = -self.L4 * c

        # the corners of the leg are offset by W from the centreline's start and end points
        leg_corners = [
            (self.W * c, self.W * s),
            (-self.W * c, -self.W * s),
            (finch_x - self.W * c, finch_y - self.W * s),
            (finch_x + self.W * c, finch_y + self.W * s),
        ]
        southern_leg_poly = Polygon(leg_corners)

        # union the two polygons to get the final shape
        final_shape = main_body_poly.union(southern_leg_poly)

        # ensure the final shape is a valid polygon
        if isinstance(final_shape, MultiPolygon):
            final_shape = max(final_shape.geoms, key=lambda g: g.area)
        elif not isinstance(final_shape, Polygon):
            final_shape = final_shape.buffer(0.0)
        if not final_shape.is_valid:
            final_shape = final_shape.buffer(0.0)

        # apply the overall rotation to the polygon
        theta = np.deg2rad(self.rotation_deg)
        cos_theta, sin_theta = np.cos(theta), np.sin(theta)
        rotation_matrix = np.array([[cos_theta, -sin_theta], [sin_theta, cos_theta]], dtype=np.float64)

        polygon_coords = np.asarray(final_shape.exterior.coords)
        polygon_rotated = polygon_coords @ rotation_matrix

        # calculate coordinates for MACAW and ALB to ensure equidistant routing from boundary
        diagonal_offset = self.D + self.W * (1.0 - np.sqrt(2.0))

        # create the fixes coordinates
        fixes_coords = {
            "EGL": np.array([0, 0]),
            "QUAIL": np.array([self.L2, 0]),
            "SWIFT": np.array([self.L2 + self.F, 0]),
            "GOOSE": np.array([0, self.L3]),
            "PEL": np.array([0, self.L3 + self.F]),
            "CRANE": np.array([-self.L1, 0]),
            "HERON": np.array([-self.L1 - self.F, 0]),
            "FINCH": np.array([finch_x, finch_y]),
            "ROBIN": np.array([(self.L4 + self.F) * s, -(self.L4 + self.F) * c]),
            "ALB": np.array([0, diagonal_offset]),
            "MACAW": np.array([diagonal_offset, 0]),
        }

        # apply the overall rotation to all fixes
        for name, xy in fixes_coords.items():
            fixes_coords[name] = xy @ rotation_matrix

        # convert to lat/lon coordinates using the approximation that one degree is approximately 60 nautical miles
        DEGREE_LAT_NM = 60.0
        lat_scale = self.half_width_nmi / DEGREE_LAT_NM
        cos_lat_origin_rad = np.cos(np.deg2rad(self.origin_lat))
        lon_scale = lat_scale / cos_lat_origin_rad

        # convert polygon coordinates to lat/lon
        polygon_latlons = np.zeros_like(polygon_rotated)
        polygon_latlons[:, 0] = polygon_rotated[:, 1] * lat_scale + self.origin_lat
        polygon_latlons[:, 1] = polygon_rotated[:, 0] * lon_scale + self.origin_lon

        # convert fix coordinates to lat/lon
        fixes_dict: dict[str, Pos2D] = {}
        for fix_name, xy in fixes_coords.items():
            lat = xy[1] * lat_scale + self.origin_lat
            lon = xy[0] * lon_scale + self.origin_lon
            fixes_dict[fix_name] = Pos2D(lat=lat, lon=lon)

        # create polygon and buffer to ensure valid geometry
        poly = Polygon(polygon_latlons).buffer(0.0)
        coords_pos2d = [Pos2D(lat=latlon[0], lon=latlon[1]) for latlon in poly.exterior.coords]

        # create the airspace: (area -> volume -> sector) + fixes
        area = Area(coords_pos2d)
        volume = Volume(area, self.fl_limits[0], self.fl_limits[1])
        sector = Sector([volume])
        fixes = Fixes(fixes_dict)
        airspace = Airspace({"sector_xplus": sector}, fixes)

        routes = self._create_routes(fixes_dict)

        return airspace, routes

    def _create_routes(self, fixes_dict: dict[str, Pos2D]) -> list[Route]:
        """
        Create the route network for the X-Plus sector.

        Generates a comprehensive bidirectional route network connecting the four terminal navigation fixes
        (ROBIN, HERON, PEL, SWIFT) through the central hub and intermediate fixes. Routes with turns exceeding
        the maximum turn angle are filtered out.

        Parameters
        ----------
        fixes_dict : dict[str, Pos2D]
            Dictionary mapping fix names to their positions

        Returns
        -------
        list[Route]
            List of Route objects providing terminal-to-terminal connectivity with valid turn angles

        Notes
        -----
        Route structure provides:
        - Primary connectivity: All terminal fixes connect through EGL (central hub)
        - Alternative routing: PEL<->SWIFT have an additional diagonal path via ALB->MACAW
        - Full bi-directionality: Every terminal can reach every other terminal
        - Turn angle validation: Routes with turns > max_turn_angle_deg are excluded
        """
        route_definitions = [
            # ROBIN to {HERON, PEL, SWIFT}
            ["ROBIN", "FINCH", "EGL", "CRANE", "HERON"],
            ["ROBIN", "FINCH", "EGL", "ALB", "GOOSE", "PEL"],
            ["ROBIN", "FINCH", "EGL", "MACAW", "QUAIL", "SWIFT"],
            # HERON to {PEL, SWIFT, ROBIN}
            ["HERON", "CRANE", "EGL", "ALB", "GOOSE", "PEL"],
            ["HERON", "CRANE", "EGL", "MACAW", "QUAIL", "SWIFT"],
            ["HERON", "CRANE", "EGL", "FINCH", "ROBIN"],
            # PEL to {SWIFT (2 ways), ROBIN, HERON}
            ["PEL", "GOOSE", "ALB", "MACAW", "QUAIL", "SWIFT"],
            ["PEL", "GOOSE", "ALB", "EGL", "MACAW", "QUAIL", "SWIFT"],
            ["PEL", "GOOSE", "ALB", "EGL", "FINCH", "ROBIN"],
            ["PEL", "GOOSE", "ALB", "EGL", "CRANE", "HERON"],
            # SWIFT to {ROBIN, HERON, PEL (2 ways)}
            ["SWIFT", "QUAIL", "MACAW", "EGL", "FINCH", "ROBIN"],
            ["SWIFT", "QUAIL", "MACAW", "EGL", "CRANE", "HERON"],
            ["SWIFT", "QUAIL", "MACAW", "EGL", "ALB", "GOOSE", "PEL"],
            ["SWIFT", "QUAIL", "MACAW", "ALB", "GOOSE", "PEL"],
        ]

        return [Route(route) for route in route_definitions if self._is_route_valid(route, fixes_dict)]

    def _is_route_valid(self, route: list[str], fixes_dict: dict[str, Pos2D]) -> bool:
        """
        Check if a route has all turn angles within the specified limit.

        Parameters
        ----------
        route : list[str]
            List of waypoint names defining the route
        fixes_dict : dict[str, Pos2D]
            Dictionary mapping fix names to their positions

        Returns
        -------
        bool
            True if all turns in the route are <= max_turn_angle_deg, False otherwise
        """
        if len(route) < 3:
            return True

        incoming_heading = fixes_dict[route[0]].bearing_to(fixes_dict[route[1]])

        for i in range(1, len(route) - 1):
            outgoing_heading = fixes_dict[route[i]].bearing_to(fixes_dict[route[i + 1]])

            # calculate the turn angle (0-180 degrees)
            heading_diff = abs(outgoing_heading - incoming_heading)
            if heading_diff > 180:
                heading_diff = 360 - heading_diff

            # check if turn angle exceeds maximum allowed
            if heading_diff > self.max_turn_angle_deg:
                return False

            incoming_heading = outgoing_heading

        return True
