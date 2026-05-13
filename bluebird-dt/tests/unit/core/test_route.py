import json
import os
import tempfile
import pytest
from pydantic import ValidationError

from bluebird_dt.core import Fixes, Pos2D, Route

def test_instantiation_filed_and_current_kwargs() -> None:
    """
    Test we can instantiate when giving both filed and current lists.
    """
    
    route = Route(filed=["FIX1","FIX2"], current=["FIX2"])

    assert isinstance(route, Route)
    assert hasattr(route, "filed")
    assert len(route.filed) == 2
    assert hasattr(route, "current")
    assert len(route.current) == 1
    
def test_instantiation_positional_args() -> None:
    """
    Test we can instantiate without kwargs.
    """
    route = Route(["FIX1","FIX2"], ["FIX2"])

    assert isinstance(route, Route)
    assert hasattr(route, "filed")
    assert len(route.filed) == 2
    assert hasattr(route, "current")
    assert len(route.current) == 1


def test_instantiation_filed_kwarg() -> None:
    """
    Test we can instantiate when giving only filed list.
    """
    
    route = Route(filed=["FIX1","FIX2"])

    assert isinstance(route, Route)
    assert hasattr(route, "filed")
    assert len(route.filed) == 2
    assert hasattr(route, "current")
    assert route.current == route.filed
    
def test_instantiation_one_positional_arg() -> None:
    """
    Test we can instantiate with filed as only positional arg.
    """
    route = Route(["FIX1","FIX2"])

    assert isinstance(route, Route)
    assert hasattr(route, "filed")
    assert len(route.filed) == 2
    assert hasattr(route, "current")
    assert route.current == route.filed

def test_init_exceptions():
    """
    Test that we get TypeError when instantiating with invalid parameters
    """
    with pytest.raises(ValidationError):
        # no args
        Route()
    with pytest.raises(ValidationError):
        # wrong type args
        Route("A>B>C")
    with pytest.raises(TypeError):
        # too many args
        Route(["A","B","C"],["A"],["B"])

def test_str():
    """
    Test the string representation
    """
    r = Route(["A","B","C"])
    expected_string = "Filed: A>B>C Current: A>B>C"
    assert str(r) == expected_string


def test_eq():
    """
    Create two instances with the same filed and current routes, check they are equal.
    """
    r1 = Route(filed=["A", "B", "C"], current=["B","C"])
    r2 = Route(current=["B", "C"], filed=["A","B","C"])
    assert r1 == r2

def test_neq():
    """
    Create two instances with the same filed and different current routes, check they are not equal.
    """
    r1 = Route(filed=["A", "B", "C"], current=["A","B","C"])
    r2 = Route(current=["B", "C"], filed=["A","B","C"])
    assert r1 != r2


def test_json_round_trip():
    """
    Create a route, write to JSON, read from JSON, check equality.
    """
    r1 = Route(filed=["A","B","C"])
    j = r1.to_json()
    r2 = Route.from_json(j)
    assert r1 == r2


def test_segments_length_and_dists_to_end():
    """
    Create a route and test that segments and route distance are as expected.
    Note that Pos2D.distance returns 60NM for 1 degree of longitude (at the equator)
    """
    fixes = Fixes(
        {
            "A": Pos2D(0.0, 0.0),
            "B": Pos2D(0.0, 1.0),
            "C": Pos2D(0.0, 2.0),
        }
    )
    routes = Route(["A", "B", "C"])
    assert list(routes.segments()) == [("A", "B"), ("B", "C")]
    assert routes.length(fixes) == pytest.approx(120.0, abs=0.5)

    dists = routes.dists_to_end(fixes)
    assert dists["C"] == pytest.approx(0.0, abs=1e-6)
    assert dists["B"] == pytest.approx(60.0, abs=0.5)
    assert dists["A"] == pytest.approx(120.0, abs=0.5)


def test_add_origin_destination_to_filed_route():
    """
    Check that we can add origin and destination fixes to a route and that it's idempotent.
    """
    route = ["B"]
    updated = Route.add_origin_destination_to_filed_route(route, origin="A", dest="C")
    assert updated == ["A", "B", "C"]

    unchanged = Route.add_origin_destination_to_filed_route(["A", "B", "C"], origin="A", dest="C")
    assert unchanged == ["A", "B", "C"]


def test_load_from_file_roundtrip():
    """
    Create a route, write to file then read from file and check it's the same
    """
    r = Route(["A", "B"])
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "route.json")
        with open(path, "w") as fd:
            fd.write(json.dumps(r.data()))

        loaded = Route.load(path)
        assert loaded == r
