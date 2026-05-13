import pytest
import numpy as np

from bluebird_dt.core import Area, Sector, Pos3D, Volume

def test_init(random_adjacent_volumes):
    volumes = random_adjacent_volumes()
    sector = Sector(volumes)
    assert isinstance(sector, Sector)

def test_contains(random_sector, random_pos3d):
     sector = random_sector()
     point = random_pos3d()
     expect_contains = False
     # see if the point is within the sector's volumes
     for vol in sector.volumes:
         expect_contains |= vol.contains(point)
     assert sector.contains(point) == expect_contains


def test_boundary(random_sector):
    sector = random_sector()
    area = sector.boundary()
    assert isinstance(area, Area)
    


def test_contains_laterally(random_sector, random_pos2d):
    sector = random_sector()
    point = random_pos2d()
    area = sector.boundary()
    assert sector.contains_laterally(point) == area.contains(point)


def test_get_bounds(random_sector):
    sector = random_sector()
    bounds = sector.get_bounds()
    assert isinstance(bounds, tuple)
    assert len(bounds) == 2
    for b in bounds:
        assert isinstance(b, np.ndarray)
        assert b.shape == (3,)


def test_centre(random_sector):
    sector = random_sector()
    centre = sector.centre
    assert isinstance(centre, Pos3D)
    # centre must be within the sector
    assert sector.contains(centre)


def test_distance(random_sector, random_pos2d):
    sector = random_sector()
    point = random_pos2d()
    distance = sector.distance(point)
    assert isinstance(distance, float)
    assert distance > 0.
