import math

import numpy as np

from bluebird_dt.utility.constants import PHI0, R_E_WGS84, THETA0, F
from bluebird_dt.utility.convert import NMI_TO_M


def geodesic_to_conformal(phi: float, phi0: float = PHI0) -> float:
    tan_phi = np.tan(phi / 360 * 2 * math.pi)
    sin_phi0 = np.sin(phi0 / 360 * 2 * math.pi)

    e2 = F * (2 - F)
    A = np.sqrt(1 + (1 - e2) * tan_phi * tan_phi)
    K = e2 * sin_phi0 / np.sqrt(1 - e2 * sin_phi0 * sin_phi0)

    correction = (e2 * tan_phi - K * A) / (A * A + K * A * tan_phi)
    return phi - correction * 360 / (2 * math.pi)


def conformal_to_xy(phi_prime: float, theta: float, phi0: float = PHI0, theta0: float = THETA0) -> tuple[float, float]:
    sin_phi_prime = np.sin(phi_prime / 360 * 2 * math.pi)
    cos_phi_prime = np.cos(phi_prime / 360 * 2 * math.pi)

    sin_phi0 = np.sin(phi0 / 360 * 2 * math.pi)
    cos_phi0 = np.cos(phi0 / 360 * 2 * math.pi)

    e2 = F * (2 - F)
    R_c = R_E_WGS84 / np.sqrt(1 - e2 * sin_phi0 * sin_phi0)

    sin_theta_theta0 = np.sin((theta - theta0) / 360 * 2 * math.pi)
    cos_theta_theta0 = np.cos((theta - theta0) / 360 * 2 * math.pi)

    x = (2 * R_c * cos_phi_prime * sin_theta_theta0) / (
        1 + sin_phi0 * sin_phi_prime + cos_phi0 * cos_phi_prime * cos_theta_theta0
    )
    y = (
        2
        * R_c
        * (cos_phi0 * sin_phi_prime - sin_phi0 * cos_phi_prime * cos_theta_theta0)
        / (1 + sin_phi0 * sin_phi_prime + cos_phi0 * cos_phi_prime * cos_theta_theta0)
    )

    return (x, y)


def lon_lat_to_x_y_km(lon: float, lat: float) -> tuple[float, float]:
    """Map arrays of longitude and latitude to vectors of xy coordinates in km.

    Parameters
    ----------
    lon : ndarray
        Array of longitudes
    lat : ndarray
        Array of latitudes

    Returns
    -------
    x, y  :  ndarrays of (x, y) coordinates in km
    """
    phi_prime = geodesic_to_conformal(lat)
    x, y = conformal_to_xy(phi_prime, lon)
    return x / 1000, y / 1000


def lon_lat_to_x_y_nm(lon: float, lat: float) -> tuple[float, float]:
    """Map arrays of longitude and latitude to vectors of xy coordinates in nautical miles

    Parameters
    ----------
    lon : ndarray
        Array of longitudes
    lat : ndarray
        Array of latitudes

    Returns
    -------
    x, y  :  ndarrays of (x, y) coordinates in nautical miles
    """
    x, y = lon_lat_to_x_y_km(lon, lat)
    return x * 1000 / NMI_TO_M, y * 1000 / NMI_TO_M


def lonlat_to_xy_km(lonlat: np.ndarray[float]) -> np.ndarray[float]:
    """Map a array of long,lat coordinates to an array of NATS xy coordinates in km.

    Parameters
    ----------
    lonlat : ndarray, shape (N,2)
        Array of N (longitude, latitude) pairs

    Returns
    -------
    xy  :  ndarray, shape (N,2)
        Array of (x, y) coordinates in km
    """
    assert len(lonlat.shape) > 1
    phi_prime = geodesic_to_conformal(lonlat[:, 1])
    x, y = conformal_to_xy(phi_prime, lonlat[:, 0])
    xy = np.vstack((x, y)).T
    return xy / 1000


def lonlat_to_xy_nm(lonlat: np.ndarray[float]) -> np.ndarray[float]:
    """Map a array of lat, long coordinates to an array of NATS xy coordinates in nautical miles.

    Parameters
    ----------
    lonlat : ndarray, shape (N,2)
        Array of N (longitude, latitude) pairs

    Returns
    -------
    xy  :  ndarray, shape (N,2)
        Array of (x, y) coordinates in nautical miles
    """
    xy = lonlat_to_xy_km(lonlat)
    return xy * 1000 / NMI_TO_M
