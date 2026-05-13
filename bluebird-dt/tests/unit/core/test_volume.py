import pytest

from bluebird_dt.core.area import Area
from bluebird_dt.core.pos3d import Pos3D

from bluebird_dt.core.volume import Volume

def test_init_no_args():
    with pytest.raises(TypeError):
        v = Volume()
    
def test_init_invalid_fl(random_area):
    area = random_area() 
    assert isinstance(area, Area)
    with pytest.raises(ValueError):
        v = Volume(area, -10, 10)
    with pytest.raises(ValueError):
        v = Volume(area, 10, -10)

def test_init_all_positional_args(random_area):
    area = random_area()
    v = Volume(area, 100, 200, "SECTOR", "dummy description", "FIX1_FIX2")
    assert isinstance(v, Volume)
    assert v.sector_name == "SECTOR"
    assert v.description == "dummy description"
    assert v.airspace_id == "FIX1_FIX2"


def test_init_all_kwargs(random_area):
    area = random_area()
    v = Volume(
        area=area, 
        min_fl=100, 
        max_fl=200, 
        sector_name="SECTOR", 
        description="dummy description", 
        airspace_id="FIX1_FIX2"
    )
    assert isinstance(v, Volume)
    assert v.sector_name == "SECTOR"
    assert v.description == "dummy description"
    assert v.airspace_id == "FIX1_FIX2"


def test_centre_fl(random_area):
    """
    Test that the "centre" is correct in FL.
    """
    area = random_area()
    v = Volume(area, 100, 300)
    c = v.centre
    assert isinstance(c, Pos3D)
    assert c.fl == 200