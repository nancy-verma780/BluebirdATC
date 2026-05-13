import random

import numpy as np
from scipy.spatial import Delaunay
from typing_extensions import override

from bluebird_dt.airspace_generator.airspace_generator import AirspaceGenerator
from bluebird_dt.core import Airspace, Area, Fixes, Pos2D, Route, Sector
from bluebird_dt.utility import graph
from bluebird_dt.utility.geo_helper import GeoHelper


class Thunderdome(AirspaceGenerator):
    """
    Thunderdome scenario.
    """

    def __init__(
        self,
        radius: float,
        fl_limits: tuple[float, float],
        num_inner: int,
        num_outer: int,
    ):
        """
        Construct a new instance.

        Parameters
        ----------
        radius: float
            Airspace radius [nmi].
        fl_limits: list[float]
            The [min, max] flight level limits allowed in the Sector.
        num_inner: int
            Maximum number of inner Fixes (any inner Fixes with no Route passing through them are removed).
        num_outer: int
            Number of outer Fixes.
        """

        if radius < 0:
            raise ValueError("Radius must be positive.")

        if (fl_limits[0] < 0) or (fl_limits[1] < 0):
            raise ValueError("Flight level limits must be positive.")

        if fl_limits[0] >= fl_limits[1]:
            raise ValueError("Maximum flight level must exceed minimum flight level.")

        if num_inner < 4:
            raise ValueError("There must be at least four inner fixes.")

        if num_outer < 2:
            raise ValueError("There must be at least two outer fixes.")

        self.radius = radius
        self.fl_limits = fl_limits
        self.num_inner = num_inner
        self.num_outer = num_outer

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

        # Convert radius to deg - lat assuming origin (0, 0)
        geo_helper = GeoHelper()
        self.radius = geo_helper.inverse_projection((self.radius, 0.0), ndigits=4).lat

        [min_fl, max_fl] = self.fl_limits

        # Generate the Sector.
        boundary = []
        boundary_edges = 3 * self.num_outer
        d_theta = (2.0 * np.pi) / boundary_edges
        for i in range(boundary_edges):
            theta = i * d_theta
            rho = max(0.75, min(0.85, random.gauss(0.8, 0.2))) * self.radius
            boundary.append(Pos2D(rho * np.cos(theta), rho * np.sin(theta)))

        sectors = {"thunderdome": Sector([Volume(Area(boundary), int(min_fl), int(max_fl))])}

        # Generate the Fixes.
        edges = []
        inner_fixes = {}
        d_theta = (2.0 * np.pi) / (self.num_inner + 1)
        offset = 2.0 * np.pi * random.random()
        for i in range(self.num_inner):
            theta = offset + (i * d_theta)
            rho = max(0.1, min(0.6, random.gauss(0.4, 0.2))) * self.radius
            inner_fixes[f"IN{i}"] = Pos2D(rho * np.cos(theta), rho * np.sin(theta))

        boundary_fixes = {}
        airport_fixes = {}
        d_theta = (2.0 * np.pi) / self.num_outer
        for i in range(self.num_outer):
            theta = (i + 0.5) * d_theta
            a = boundary[(3 * i) + 1]
            b = boundary[(3 * i) + 2]
            airport_name = f"PORT{i}"
            boundary_name = f"BOND{i}"
            airport_fixes[airport_name] = Pos2D(self.radius * np.cos(theta), self.radius * np.sin(theta))
            boundary_fixes[boundary_name] = Pos2D((a.lat + b.lat) * 0.5, (a.lon + b.lon) * 0.5)
            edges.append([airport_name, boundary_name])

        # Generate the Routes.
        non_airport_fixes = {**inner_fixes, **boundary_fixes}
        points = [[fix.lat, fix.lon] for fix in non_airport_fixes.values()]
        non_airport_fix_names = list(non_airport_fixes)
        for a, b, c in Delaunay(points).simplices:
            edges.append([non_airport_fix_names[a], non_airport_fix_names[b]])
            edges.append([non_airport_fix_names[b], non_airport_fix_names[c]])
            edges.append([non_airport_fix_names[c], non_airport_fix_names[a]])
        for edge in reversed(edges):
            if (edge[0] in boundary_fixes) and (edge[1] in boundary_fixes):
                edges.remove(edge)

        network = graph.build_from_edges(edges)
        routes = []
        for airport in airport_fixes:
            for destination in [random.choice(list(airport_fixes.keys()))]:
                if airport == destination:
                    continue
                try:
                    route = graph.shortest_path(network, airport, destination)
                    routes.append(Route(route))
                except ValueError:
                    continue

        for name in list(inner_fixes):
            used = False
            for route in routes:
                if name in route.filed:
                    used = True
            if not used:
                inner_fixes.pop(name)
        fixes = Fixes({**inner_fixes, **boundary_fixes, **airport_fixes})

        return Airspace(sectors, fixes), routes
