from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, overload

import numpy as np
from numpy.typing import NDArray
from pydantic import BaseModel, field_validator
from typing_extensions import override

from bluebird_dt.core.pos2d import Pos2D
from bluebird_dt.mixin import Comparison

# avoid circular imports
if TYPE_CHECKING:
    from bluebird_dt.core.pos4d import Pos4D


class Pos3D(BaseModel, Comparison):
    """
    Three-dimensional (latitude, longitude, flight level) position over the globe.
    """

    lat: float
    lon: float
    fl: float

    @field_validator("lat")
    def validate_lat(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be in the range [-90, +90] degrees.")
        return value

    @field_validator("lon")
    def validate_lon(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be in the range [-180, +180] degrees.")
        return value

    # For compatibility with old code, constructor that instantiates this class without keyword args
    @overload
    def __init__(self, lat: float, lon: float, fl: float) -> None: ...

    @overload
    def __init__(self, *, lat: float, lon: float, fl: float) -> None: ...

    def __init__(self, *args: float, **kwargs: Any) -> None:
        """
        Construct a new instance.

        Parameters
        ----------
        lat: float
            The latitude of the position [deg].
        lon: float
            The longitude of the position [deg].
        fl: float
            The altitude of the position in flight levels (FL).

        Examples
        --------
        >>> pos = Pos3D(50.7, -3.5, 120)
        """
        if args and not kwargs:
            if len(args) != 3:
                raise TypeError("Pos3D() takes exactly 3 positional arguments: lat, lon, fl")
            kwargs = {"lat": args[0], "lon": args[1], "fl": args[2]}
        super().__init__(**kwargs)

    @property
    def location(self) -> NDArray[np.float]:
        return np.array([self.lat, self.lon, self.fl])

    @staticmethod
    def from_str(s: str) -> Pos3D:
        """
        Construct a new instance from a string representation.

        Parameters
        ----------
        s: str
            A string representation of Pos3D.

        Returns
        --------
        Pos3D

        Examples
        --------
        >>> Pos3D("10.0S 5.0E 120FL")
        """

        s.strip()
        [lat, lon, fl] = s.split()

        pos2d = Pos2D.from_str(f"{lat} {lon}")

        if fl[-2:] != "FL":
            raise ValueError(f"Invalid flight level string: {fl}")

        return Pos3D(lat=pos2d.lat, lon=pos2d.lon, fl=float(fl[:-2]))

    @staticmethod
    def from_array(a: np.ndarray) -> Pos3D:
        """
        Construct a new instance from a numpy array.

        Parameters
        ----------
        a: np.ndarray
            A (3,) numpy array containing the latitude, longitude and flight level.

        Returns
        --------
        Pos3D
        """

        if a.shape != (3,):
            raise ValueError(f"Expected array shape (3,), given: {a.shape}")

        lat, lon, fl = a
        return Pos3D(lat=lat, lon=lon, fl=fl)

    @staticmethod
    def from_json(s: str) -> Pos3D:
        """
        Construct a new instance from a json representation.

        Parameters
        ----------
        s: str
            A json representation of Pos3D.location array [lat, lon, fl]

        Returns
        --------
        Pos3D

        Examples
        ----------
        >>> Pos3D.from_json("[1.0, 0.0, 200]")
        """

        data = json.loads(s)
        return Pos3D.from_array(np.array(data))

    def to_json(self) -> str:
        """
        Serialise the instance to JSON string.

        Returns
        --------
        str
        """

        return json.dumps([self.lat, self.lon, self.fl])

    @staticmethod
    def load(filename: str) -> Pos3D:
        """
        Construct a new instance from a file.

        Parameters
        ----------
        filename: str
            Path to a JSON file with a Pos3D definition in a dictionary format.

        Returns
        --------
        Pos3D
        """

        with open(filename) as fd:
            return Pos3D.from_json(fd.read())

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

    @override
    def __str__(self) -> str:
        """
        Create a human-readable representation of the instance.

        Returns
        --------
        str
            A string representation of Pos3D (e.g. "10.0S 5.0E 120FL")
        """

        return f"{self.pos2d()} {self.fl}FL"

    def __round__(self, precision: int) -> Pos3D:
        """
        Round the position elements to the given precision.

        Parameters
        ----------
        precision: int
            The precision in decimal digits.

        Returns
        --------
        Pos3D
        """

        return Pos3D.from_array(np.round([self.lat, self.lon, self.fl], precision))

    def pos2d(self) -> Pos2D:
        """
        Get the two-dimensional location of the position.

        Returns
        ----------
        Pos2D
        """

        return Pos2D(lat=self.lat, lon=self.lon)

    def pos4d(self, time: float) -> Pos4D:
        """
        Create a four-dimensional control-point of the position with a given time [sec].

         Parameters
        ----------
        time: float
            The time in seconds to be used for the 4D location.

        Returns
        ----------
        Pos4D
        """

        from .pos4d import Pos4D

        return Pos4D(lat=self.lat, lon=self.lon, fl=self.fl, time=time)

    def forward(self, dist: float, heading: float) -> Pos3D:
        """
         Determine the three-dimensional position
         a given distance away [nmi] following a given heading [deg].
         Flight level is maintained.

        Parameters
         ----------
         dist: float
             The distance to be used in nautical miles.
         heading: float
             The heading to be used in degrees.

         Returns
         ----------
         Pos3D
        """

        proj_pos2d = self.pos2d().forward(dist, heading)

        return Pos3D(lat=proj_pos2d.lat, lon=proj_pos2d.lon, fl=self.fl)

    def bearing_to(self, other: Pos2D | Pos3D) -> float:
        """
        Calculate the bearing [deg] to another location.

        Parameters
        ----------
        other: Union[Pos2D, Pos3D]
            The other location to be used.

        Returns
        ----------
        float
            Bearing in degrees.
        """

        if isinstance(other, Pos3D):
            other = other.pos2d()
        return self.pos2d().bearing_to(other)

    def distance(self, other: Pos2D | Pos3D) -> float:
        """
        Calculate the lateral geodesic distance [nmi] to another position.
        Flight level is NOT considered (if provided in Pos3D).

        Parameters
        ----------
        other: Union[Pos2D, Pos3D]
            The other location to be used.

        Returns
        ----------
        float
            Distance in nautical miles.
        """

        if isinstance(other, Pos3D):
            other = other.pos2d()
        return self.pos2d().distance(other)

    @override
    def __eq__(self, other: Pos3D) -> bool:
        """
        Check if two positions are equal.

        Parameters
        ----------
        other: Pos3D
            The other position to be used.

        Returns
        ----------
        bool
        """
        return np.allclose([self.lat, self.lon, self.fl], [other.lat, other.lon, other.fl])

    @override
    def __hash__(self) -> int:
        """
        Compute the hash value of the position.
        """
        return hash((self.lat, self.lon, self.fl))
