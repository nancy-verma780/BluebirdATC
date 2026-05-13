from __future__ import annotations

import json
import typing
from dataclasses import dataclass, field

from shapely import MultiPolygon, Polygon, unary_union
from shapely.geometry import LineString

from bluebird_dt.core.area import Area
from bluebird_dt.core.fixes import Fixes
from bluebird_dt.core.pos2d import Pos2D
from bluebird_dt.core.sector import Sector
from bluebird_dt.core.volume import Volume
from bluebird_dt.mixin import Comparison


@dataclass(init=True)
class AirwayLeg(Comparison):
    """
    Represents a single segment of a navigational airway, connecting two fixes.

    An AirwayLeg defines a directed segment between a starting point (`p0`) and an ending point (`p1`), identified by
    both `Pos2D` coordinates and string identifiers (`p0_identifier`, `p1_identifier`). It encapsulates the
    vertical constraints for this segment through `upper_limit_fl` and `lower_limit_fl`.

    Attributes
    ----------
    upper_limit_fl : int
        The upper flight level boundary for this leg.
    lower_limit_fl : int
        The lower flight level boundary for this leg.
    p0 : Pos2D
        The geographical starting point (fix) of the leg.
    p0_identifier : str
        The unique string identifier for the starting fix (`p0`).
    p1 : Pos2D
        The geographical ending point (fix) of the leg.
    p1_identifier : str
        The unique string identifier for the ending fix (`p1`).

    Methods
    -------
    data()
        Returns a dictionary representation suitable for JSON serialization.
    to_json()
        Serializes the object to a JSON string.
    from_json(data: str) -> AirwayLeg
        Deserializes an AirwayLeg from a JSON string.
    volume(half_width: float = 0.08) -> Volume | None
        Calculates or retrieves the spatial volume for the leg.
    """

    upper_limit_fl: int
    lower_limit_fl: int
    p0: Pos2D
    p0_identifier: str
    p1: Pos2D
    p1_identifier: str

    def data(self) -> dict[str, typing.Any]:
        """
        Returns a dictionary representation of the AirwayLeg object.

        This dictionary includes the start and end fix identifiers and the data representations of the start and end
        `Pos2D` objects the upper and lower flight level limits.

        This structure is designed to be directly serializable to JSON using `json.dumps`.

        Returns
        -------
        dict[str, typing.Any]
            A dictionary containing the leg's attributes suitable for serialization.
        """
        return {
            "p0_identifier": self.p0_identifier,
            "p1_identifier": self.p1_identifier,
            "p0": str(self.p0),
            "p1": str(self.p1),
            "upper_limit_fl": self.upper_limit_fl,
            "lower_limit_fl": self.lower_limit_fl,
        }

    def to_json(self) -> str:
        """
        Serializes the AirwayLeg object into a JSON string representation.

        Returns
        -------
        str
            A JSON string representing the AirwayLeg object.
        """
        return json.dumps(self.data(), indent=4)

    @staticmethod
    def from_json(data: str) -> AirwayLeg:
        """
        Constructs an AirwayLeg object from a JSON string representation.

        Parses the JSON string to extract leg attributes, including flight levels, fix identifiers, fix coordinates
        (by calling `Pos2D.from_json`).

        Parameters
        ----------
        data : str
            A JSON string representing the AirwayLeg object.

        Returns
        -------
        AirwayLeg
            A new instance of the AirwayLeg class populated with data from the JSON string.
        """
        data_dict: dict[str, typing.Any] = json.loads(data)

        p0 = Pos2D.from_str(data_dict["p0"])
        p1 = Pos2D.from_str(data_dict["p1"])

        return AirwayLeg(
            data_dict["upper_limit_fl"],
            data_dict["lower_limit_fl"],
            p0,
            data_dict["p0_identifier"],
            p1,
            data_dict["p1_identifier"],
        )

    def volume(self, half_width: float = 0.08) -> Volume | None:
        """
        Generates or retrieves the spatial Volume for this airway leg.

        This method determines the 3D volume associated with the leg based on a buffering the leg's 2D centreline
        (a LineString from `p0` to `p1`) by
        the specified `half_width` (in degrees) to create a polygonal `Area`. This `Area` is then combined with the
        leg's `lower_limit_fl` and `upper_limit_fl` to form the final `Volume`.

        Parameters
        ----------
        half_width : float, optional
            The half-width in degrees to buffer the leg's centreline if a default volume needs to be generated.
            Defaults to 0.08.

        Returns
        -------
        Volume | None
            The calculated Volume object for the leg or if
            default volume generation fails (e.g., due to invalid geometry).
        """

        centerline = LineString([(self.p0.lat, self.p0.lon), (self.p1.lat, self.p1.lon)])
        buffered_poly = centerline.buffer(half_width)
        lats, lons = buffered_poly.exterior.coords.xy
        pos2d_list = [Pos2D(point[0], point[1]) for point in zip(lats, lons, strict=False)]

        return Volume(Area(pos2d_list), self.lower_limit_fl, self.upper_limit_fl)


@dataclass(init=True)
class Airway(Comparison):
    """
    Represents a navigational airway defined by a sequence of connected legs.

    An airway consists of an identifier and an ordered list of `AirwayLeg` objects.
    Each leg connects two fixes and has associated upper and lower flight level limits.

    This class provides methods to construct airways from fix sequences, serialize/deserialize them to/from JSON,
    extract the sequence of fix identifiers or coordinates, and generate 3D spatial volumes representing the airway's
    extent, with options for merging adjacent segments and trimming against sector boundaries.

    Attributes
    ----------
    identifier : str
        The unique identifier for the airway (e.g., "UL607").
    _legs : list[AirwayLeg]
        An ordered list of `AirwayLeg` objects defining the path and vertical limits of the airway segments.

    Methods
    -------
    from_list_of_fixes(identifier, fix_names, lower_limit_fl, upper_limit_fl, fixes)
        Constructs an Airway from a list of fix names and flight level limits.
    data()
        Returns a dictionary representation suitable for JSON serialization.
    to_json()
        Serializes the object to a JSON string.
    from_json(data: str) -> Airway
        Deserializes an Airway from a JSON string.
    fixes()
        Extracts the sequence of fix identifiers defining the airway path.
    coords()
        Extracts the sequence of coordinates defining the airway path.
    volumes(half_width=0.08, inside_sector=None, outside_sector=None)
        Generates a list of Volume objects representing the spatial extent.
    """

    identifier: str
    _legs: list[AirwayLeg] = field(default_factory=list)

    @staticmethod
    def from_list_of_fixes(
        identifier: str,
        fix_names: list[str],
        lower_limit_fl: int,
        upper_limit_fl: int,
        fixes: Fixes,
    ) -> Airway:
        """
        Constructs an Airway object from a sequence of fix names and flight level limits.

        This method creates an Airway by defining a series of AirwayLeg objects connecting consecutive fixes specified
        in `fix_names`. It uses the provided `fixes` object to look up the `Pos2D` coordinates for each fix name.

        Each generated leg is assigned the specified `lower_limit_fl` and `upper_limit_fl`.

        If a fix name listed in `fix_names` is not found in the `fixes` object, the corresponding leg involving that
        fix is skipped.

        Parameters
        ----------
        identifier : str
            The unique identifier for the airway being created.
        fix_names : list[str]
            An ordered list of fix identifiers (strings) defining the path of the airway.
            Must contain at least two fix names to create any legs.
        lower_limit_fl : int
            The lower flight level limit for all legs of the airway.
        upper_limit_fl : int
            The upper flight level limit for all legs of the airway.
        fixes : Fixes
            A `Fixes` object containing the mapping from fix identifiers to `Pos2D` coordinates.

        Returns
        -------
        Airway
            A new Airway object constructed from the specified fixes and limits.
        """
        legs: list[AirwayLeg] = []

        # iterate through pairs of fix names to create legs
        for i in range(len(fix_names) - 1):
            fix0_name = fix_names[i]
            fix1_name = fix_names[i + 1]

            # check if both fixes exist
            if fix0_name not in fixes.places or fix1_name not in fixes.places:
                continue

            # Get the Pos2D objects for the fixes
            p0 = fixes.places[fix0_name]
            p1 = fixes.places[fix1_name]

            legs.append(AirwayLeg(upper_limit_fl, lower_limit_fl, p0, fix0_name, p1, fix1_name))

        return Airway(identifier, legs)

    def data(self) -> dict[str, typing.Any]:
        """
        Returns a dictionary representation of the Airway object.

        This representation includes the airway's identifier and a list of dictionary representations of its
        constituent AirwayLeg objects. This format is suitable for JSON serialization.

        Returns
        -------
        dict[str, typing.Any]
            A dictionary containing the airway's identifier and a list of leg data dictionaries.
        """
        return {
            "identifier": self.identifier,
            "legs": [leg.data() for leg in self._legs],
        }

    def to_json(self) -> str:
        """
        Serializes the Airway object into a JSON string representation.

        Returns
        -------
        str
            A JSON string representing the Airway object.
        """
        return json.dumps(self.data(), indent=4)

    @staticmethod
    def from_json(data: str) -> Airway:
        """
        Constructs an Airway object from a JSON string representation.

        Parameters
        ----------
        data : str
            A JSON string representing the Airway object.

        Returns
        -------
        Airway
            A new instance of the Airway class populated with data from the JSON string.
        """
        data_dict: dict[str, typing.Any] = json.loads(data)

        legs = [AirwayLeg.from_json(json.dumps(leg)) for leg in data_dict["legs"]]

        return Airway(data_dict["identifier"], legs)

    def fixes(self) -> list[str]:
        """
        Extracts the sequence of fix identifiers defining the airway path.

        Iterates through the ordered airway legs and collects the start fix identifier of the first leg, followed by the
        end fix identifiers of all subsequent legs. Ensures that the legs form a continuous path by checking if the end
        fix identifier of one leg matches the start fix identifier of the next using the previously added identifier.

        Returns
        -------
        list[str]
            A list of fix identifiers (strings) along the airway in order.
            Returns an empty list if the airway has no legs.

        Raises
        ------
        ValueError
            If the airway legs are not ordered sequentially (i.e., the start fix identifier of a leg does not match the
            end fix identifier of the previous leg stored in the output list).
        """
        if len(self._legs) == 0:
            return []

        output = [self._legs[0].p0_identifier]

        for leg in self._legs:
            if leg.p0_identifier != output[-1]:
                raise ValueError("Incorrectly ordered airway legs")

            output.append(leg.p1_identifier)

        return output

    def coords(self) -> list[Pos2D]:
        """
        Extracts the sequence of coordinates defining the airway path.

        Iterates through the ordered airway legs and collects the start point of the first leg, followed by the end
        points of all subsequent legs.

        Returns
        -------
        list[Pos2D]
            A list of Pos2D objects representing the coordinates of the waypoints along the airway in order.
            Returns an empty list if the airway has no legs.

        Raises
        ------
        ValueError
            If the airway legs are not ordered sequentially (i.e., the end point of a leg does not match the start
            point of the subsequent leg).
        """
        if len(self._legs) == 0:
            return []

        output = [self._legs[0].p0]
        latest_waypoint: str = self._legs[0].p0_identifier

        for leg in self._legs:
            if leg.p0_identifier != latest_waypoint:
                raise ValueError("Incorrectly ordered airway legs")

            latest_waypoint = leg.p1_identifier
            output.append(leg.p1)

        return output

    def volumes(
        self,
        half_width: float = 0.08,
        inside_sector: Sector | None = None,
        outside_sector: Sector | None = None,
    ) -> list[Volume]:
        """
        Generates a list of Volume objects representing the spatial extent of the airway.

        This method first creates a Volume for each leg of the airway. It then merges adjacent volumes that share the
        same flight level limits. Finally, if `inside_sector` or `outside_sector` are provided, the volumes are trimmed
        to lie within or outside the specified sector boundaries, respectively.

        Parameters
        ----------
        half_width : float, optional
            The half-width in degrees to buffer each airway leg's centreline to create its volume.
            Defaults to 0.08 degrees.
        inside_sector : Sector | None, optional
            If provided, the resulting volumes will be trimmed to include only the parts that fall inside the lateral
            boundary of this sector. Defaults to None.
        outside_sector : Sector | None, optional
            If provided, the resulting volumes will be trimmed to include only the parts that fall outside the lateral
            boundary of this sector. Defaults to None.

        Returns
        -------
        list[Volume]
            A list of Volume objects representing the merged and potentially trimmed spatial extent of the airway.
        """

        # create the volumes, keeping only the non-None ones
        all_volumes_and_legs = [(leg, leg.volume(half_width=half_width)) for leg in self._legs]
        volumes_and_legs = [(leg, volume) for (leg, volume) in all_volumes_and_legs if volume is not None]

        # merge the volumes
        merged_volumes = Airway._merge_volumes([volume for _, volume in volumes_and_legs])

        if inside_sector is not None:
            merged_volumes = Airway._trim_to_sector(merged_volumes, inside_sector, inside=True)

        if outside_sector is not None:
            merged_volumes = Airway._trim_to_sector(merged_volumes, outside_sector, inside=False)

        return merged_volumes

    @staticmethod
    def _trim_to_sector(
        volumes: list[Volume],
        sector: Sector,
        inside: bool = True,
        area_threshold_deg: float = 0.05,
    ) -> list[Volume]:
        """
        Trims a list of volumes to lie either inside or outside a given sector's lateral boundary.

        This method takes a list of input volumes and a sector. It calculates the intersection or difference of each
        volume's area with the sector's boundary polygon.

        If a trimming operation (intersection or difference) results in a MultiPolygon (meaning the original volume is
        split into multiple disjoint parts by the sector boundary), each resulting polygon is turned into a new Volume
        object, maintaining the original volume's flight level limits.

        Parameters
        ----------
        volumes : list[Volume]
            The list of volumes to be trimmed.
        sector : Sector
            The sector whose boundary will be used for trimming.
        inside : bool, optional
            If True (default), keeps the parts of the volumes *inside* the sector (intersection).
            If False, keeps the parts *outside* the sector (difference).
        area_threshold_deg : float, optional
            The minimum area threshold in degrees for the resulting polygons. Polygons with an area smaller than this
            threshold will be discarded. Defaults to 0.05.
            This is useful to filter out small artifacts that may result from the trimming operation.

        Returns
        -------
        list[Volume]
            A new list containing the trimmed Volume objects.
        """
        # first, extract the lateral area of the sector. to do this we have to extract the boundary of the sector
        sector_area = sector.boundary()

        # this recalculates the polygon and fixes a lot of issues with it (e.g. poorly-ordered points etc.)
        sector_poly = sector_area.boundary.buffer(0)

        assert sector_poly.is_valid, "Sector polygon is not valid polygon"

        # inside = True: trim to inside the sector
        # inside = False: trim to outside the sector
        trimmed_volumes: list[Volume] = []

        for volume in volumes:
            vol_poly = volume.area.boundary

            assert vol_poly.is_valid, "Volume polygon is not valid polygon"

            # if we're inside, take the intersection of the two polygons. otherwise, take the difference
            trimmed_poly = vol_poly.intersection(sector_poly) if inside else vol_poly.difference(sector_poly)

            assert isinstance(trimmed_poly, Polygon | MultiPolygon)

            # if it isn't a multipolygon (i.e., there is only one polygon), then we'll convert it to one.
            # this allows to treat singular and multi polygons the same way
            if isinstance(trimmed_poly, Polygon):
                trimmed_poly = MultiPolygon([trimmed_poly])

            for poly in trimmed_poly.geoms:
                # check the area of the polygon and skip it if it's too small
                if poly.area < area_threshold_deg:
                    continue

                # now we have the merged polygon, we need to create a new volume
                # with the same lower and upper flight level limits
                trimmed_volume = Volume.from_polygon(poly, volume.min_fl, volume.max_fl)
                trimmed_volumes.append(trimmed_volume)

        return trimmed_volumes

    @staticmethod
    def _merge_volumes(volumes: list[Volume]) -> list[Volume]:
        """
        Merges adjacent volumes in a list if they share the same minimum and maximum flight levels.

        This method assumes that the input list of volumes is sorted such that physically adjacent volumes appear
        consecutively in the list. It iterates through the list, grouping consecutive volumes with identical flight
        level limits. The boundaries of these grouped volumes are then merged. Volumes that cannot be merged with their
        neighbors are kept as they are.

        Parameters
        ----------
        volumes : list[Volume]
            A list of Volume objects, assumed to be sorted by physical adjacency.

        Returns
        -------
        list[Volume]
            A new list of Volume objects where adjacent volumes with matching flight level boundaries have been merged.
        """
        if len(volumes) == 0:
            return volumes

        merged_volume_list: list[Volume] = []

        # so we want to go through from the first to the last volume and merge together
        # adjacent volumes that have the same lower and upper flight level limits
        # NOTE: we assume that the volumes are sorted by physical adjacency

        # volume pointer
        vp = 0

        # while we have volumes to merge
        while vp < len(volumes):
            # get the current volume and its polygon
            start_volume = volumes[vp]
            polys_to_merge = [start_volume.area.boundary]
            min_fl = start_volume.min_fl
            max_fl = start_volume.max_fl

            # while we have volumes to merge and the current volume is adjacent to the next volume
            next_vp = vp + 1
            while next_vp < len(volumes):
                next_volume = volumes[next_vp]

                # check if the current volume and the next volume are adjacent
                if min_fl != next_volume.min_fl or max_fl != next_volume.max_fl:
                    break

                # store the next volume's polygon for merging
                polys_to_merge.append(next_volume.area.boundary)
                next_vp += 1

            # if we have merged more than one volume, we need to create a new volume
            if len(polys_to_merge) > 1:
                # merge the polygons
                merged_poly = unary_union(polys_to_merge)

                assert isinstance(merged_poly, Polygon | MultiPolygon)

                # if it isn't a multipolygon (i.e., there is only one polygon), then we'll convert it to one.
                # this allows to treat singular and multi polygons the same way
                if isinstance(merged_poly, Polygon):
                    merged_poly = MultiPolygon([merged_poly])

                # now create the volume(s) from the merged polygon and add it/them to the list
                merged_volume_list.extend([Volume.from_polygon(poly, min_fl, max_fl) for poly in merged_poly.geoms])

            # otherwise, just keep the original
            else:
                merged_volume_list.append(start_volume)

            # move the volume pointer to the next volume
            vp = next_vp

        return merged_volume_list
