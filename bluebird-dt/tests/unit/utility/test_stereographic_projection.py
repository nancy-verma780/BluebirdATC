import numpy as np

from bluebird_dt.utility.convert import NMI_TO_M
from bluebird_dt.utility.stereographic_projection import (
    lon_lat_to_x_y_km,
    lon_lat_to_x_y_nm,
    lonlat_to_xy_km,
    lonlat_to_xy_nm,
)

def test_lat_lon_to_xy(stereographic_projection_test_vals):
    lats =  stereographic_projection_test_vals[:,0]
    lons = stereographic_projection_test_vals[:,1]
    # test values have x,y in metres - convert to km for comparison
    expected_xy = stereographic_projection_test_vals[:,2:]/1000.0
    x, y = lon_lat_to_x_y_km(lons, lats)
    xy = np.vstack((x, y)).T
    assert np.allclose(xy, expected_xy, atol=0.5)

def test_lonlat_to_xy(stereographic_projection_test_vals):
    # get the second then first columns of the test_vals table
    lonlats = stereographic_projection_test_vals[:,[1,0]]
    expected_xy = stereographic_projection_test_vals[:,2:]/1000.0
    xy = lonlat_to_xy_km(lonlats)
    assert np.allclose(xy, expected_xy, atol=0.5)

def test_lon_lat_to_xy_nm(stereographic_projection_test_vals):
    lats =  stereographic_projection_test_vals[:,0]
    lons = stereographic_projection_test_vals[:,1]
    expected_xy = stereographic_projection_test_vals[:,2:]/NMI_TO_M
    x, y = lon_lat_to_x_y_nm(lons, lats)
    xy = np.vstack((x, y)).T
    assert np.allclose(xy, expected_xy, atol=0.5)

def test_lonlat_to_xy_nm(stereographic_projection_test_vals):
    latlons = stereographic_projection_test_vals[:,[1,0]]
    expected_xy = stereographic_projection_test_vals[:,2:]/NMI_TO_M
    xy = lonlat_to_xy_nm(latlons)
    assert np.allclose(xy, expected_xy, atol=0.5)