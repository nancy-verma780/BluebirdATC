import pytest

from bluebird_dt.core import Fixes, Pos2D


@pytest.fixture
def places_dict():
    return {
        "CAMBG": Pos2D(52.2069, 0.1713),
        "EXTER": Pos2D(50.7350, -3.4153),
        "HTHRW": Pos2D(51.4700, -0.4543),
        "STHPN": Pos2D(50.9515, -1.3577),
    }

def test_instantiation(places_dict) -> None:
    """
    Test correct instantiation and attributes of Fixes
    """
    visibility_dict = {
        "CAMBG": True,
        "EXTER": False,
        "HTHRW": True,
        "STHPN": False,
    }
    fixes = Fixes(places=places_dict, visibility=visibility_dict)

    assert isinstance(fixes, Fixes)
    assert hasattr(fixes, "places")
    assert fixes.places == places_dict
    assert hasattr(fixes, "visibility")
    assert fixes.visibility == visibility_dict

def test_default_visibility(places_dict) -> None:
    """
    Test default visibility when not provided
    """
    fixes = Fixes(places=places_dict)

    assert isinstance(fixes, Fixes)
    assert hasattr(fixes, "places")
    assert fixes.places == places_dict
    assert hasattr(fixes, "visibility")
    assert fixes.visibility == {name: True for name in places_dict}

def test_visibility_default_true(places_dict) -> None:
    """
    Test that if a key is in places_dict but not in visibility_dict, it still exists in the Fixes visibility with True
    """
    visibility_dict = {
        "CAMBG": True,
        "EXTER": False,
    }

    fixes = Fixes(places=places_dict, visibility=visibility_dict)

    assert fixes.visibility["CAMBG"] is True
    assert fixes.visibility["EXTER"] is False
    assert fixes.visibility["HTHRW"] is True
    assert fixes.visibility["STHPN"] is True

def test_visibility_key_error(places_dict) -> None:
    """
    Test that an error is raised when a visibility fix name is not found in places dict
    """
    visibility_dict = {
        "NONEXISTENT": False,
    }

    with pytest.raises(KeyError, match="Fix 'NONEXISTENT' not found in places"):
        Fixes(places=places_dict, visibility=visibility_dict)

def test_set_places(places_dict) -> None:
    """
    Test setting places property
    """
    new_places = {
        "NEWPLACE": Pos2D(0, 0),
    }

    fixes = Fixes(places=places_dict)
    fixes.places = new_places

    assert fixes.places == new_places
    assert fixes.as_set == set(new_places.keys())

def test_merging_fix_objects():

    fixes1 = Fixes({"P1": Pos2D(1, 1)}, {"P1": True})
    fixes2 = Fixes({"P2": Pos2D(0, 0)}, {"P2": False})
    fixes3 = Fixes({"P3": Pos2D(-1, -1)}, {"P3": False})

    fixes = fixes1 | fixes2 | fixes3

    assert fixes.visibility == {
            "P1": True,
            "P2": False,
            "P3": False,
            }

def test_override_fix_objects_on_merge():
    fixes1 = Fixes({"P1": Pos2D(1, 1)}, {"P1": True})
    fixes2 = Fixes({"P2": Pos2D(0, 0)}, {"P2": False})
    fixes3 = Fixes({"P1": Pos2D(-1, -1)}, {"P1": False})


    fixes = fixes1 | fixes2 | fixes3

    assert fixes.visibility == {
            "P1": False,
            "P2": False,
            }
    assert fixes.get("P1") == Pos2D(-1, -1)