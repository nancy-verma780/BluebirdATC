import logging
import os
import pathlib
import re

import pytest

from bluebird_dt.core import Airspace, Area, Fixes, Pos2D, Sector, Volume

from bluebird_dt.utility.airspace_data import (
    create_airspace,
    create_conditional_route_dict,
    create_sector,
    load_fixes,
    load_fixes_csv,
)

TEST_DATA_DIR = pathlib.Path(__file__).resolve().parent.parent.parent / "test_data" 

def test_create_conditional_route_dict(conditional_volumes) -> None:
    """
    Test creating a conditional route dict
    """
    crd = create_conditional_route_dict(conditional_volumes)
    assert isinstance(crd, dict)
    assert len(crd) == 2
    for k, v in crd.items():
        assert isinstance(k, str)
        assert isinstance(v, Volume) 

def test_load_fixes() -> None:
    """
    Test loading fixes from a file
    """
    fixes_data_file = os.path.join(TEST_DATA_DIR, "test_fixes.csv")
    fixes = load_fixes(fixes_data_file)
    assert isinstance(fixes, Fixes)

    with pytest.raises(NotImplementedError):
        load_fixes("unknown.ext")

def test_create_sector() -> None:
    """
    Create a sector, including conditional routes
    """
    geojson_path = os.path.join(TEST_DATA_DIR, "1.geojson")
    sector = create_sector(geojson_path)
    assert isinstance(sector, Sector)
    assert len(sector.area_of_responsibility) == 1
    assert isinstance(sector.area_of_responsibility[0], Volume)
    assert isinstance(sector.conditional_volume_dict, dict)
    assert len(sector.conditional_volume_dict) == 2
    for k, v in sector.conditional_volume_dict.items():
        assert isinstance(k, str)
        assert re.match("[A-Z1-9]+_[A-Z1-9]+", k) is not None
        assert isinstance(v, Volume)


def test_create_airspace() -> None:
    """
    Test the full chain
    """
    sector_path = os.path.join(TEST_DATA_DIR, "1.geojson")
    fixes_path = os.path.join(TEST_DATA_DIR, "test_fixes.csv")
    airspace = create_airspace([sector_path], [fixes_path])
    assert isinstance(airspace, Airspace)
    assert isinstance(airspace.sectors, dict)
    assert "1" in airspace.sectors
    assert isinstance(airspace.sectors["1"], Sector)
    assert isinstance(airspace.fixes, Fixes)


def test_load_fixes_csv(tmp_path) -> None:
    """
    Test that duplicate fixes are dropped and visibility flags are applied.
    """
    csv_path = tmp_path / "fixes.csv"
    csv_path.write_text(
        "fix,lat,lon,visible\n"
        "AAA,1.0,2.0,Y\n"
        "AAA,9.0,9.0,N\n"
        "BBB,3.0,4.0,N\n"
    )

    fixes = load_fixes_csv(str(csv_path))
    assert fixes.places["AAA"].lat == 1.0
    assert fixes.places["AAA"].lon == 2.0
    assert fixes.get_visibility("AAA") is False
    assert fixes.get_visibility("BBB") is False


def test_create_conditional_route_dict_warnings(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test warnings for missing descriptions and duplicate keys.
    """
    coords = [
        Pos2D(lat=0.0, lon=0.0),
        Pos2D(lat=0.0, lon=1.0),
        Pos2D(lat=1.0, lon=1.0),
        Pos2D(lat=0.0, lon=0.0),
    ]
    area = Area(coords)
    v1 = Volume(area, 0, 100, description=None)
    v2 = Volume(area, 0, 100, description="A")
    v3 = Volume(area, 0, 100, description="B_A")
    v4 = Volume(area, 0, 100, description="A_B")

    with caplog.at_level(logging.WARNING):
        result = create_conditional_route_dict([v1, v2, v3, v4])

    assert list(result.keys()) == ["A_B"]
    assert any("does not have a description" in record.message for record in caplog.records)
    assert any("does not contain exactly two fixes" in record.message for record in caplog.records)
    assert any("Duplicate key" in record.message for record in caplog.records)
