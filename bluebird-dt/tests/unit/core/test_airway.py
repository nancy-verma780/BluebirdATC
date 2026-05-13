import pytest

from bluebird_dt.core import Airway, AirwayLeg, Fixes, Pos2D, Sector, Volume

def test_airwayleg_init():
    """
    Instantiate AirwayLeg using keyword args
    """
    al = AirwayLeg(
        upper_limit_fl=400,
        lower_limit_fl=200,
        p0=Pos2D(0.,0.),
        p0_identifier="FIX1",
        p1=Pos2D(1.,0.),
        p1_identifier="FIX2"
    )
    assert isinstance(al, AirwayLeg)



# def test_airwayleg_init_wrong_types():
#     with pytest.raises(TypeError):
#         al = AirwayLeg(
#             upper_limit_fl=600,
#             lower_limit_fl=300,
#             p0=[0,0],
#         p0_identifier="FIX1",
#         p1=Pos2D(1.,0.),
#         p1_identifier="FIX2"
#         )

def test_airway_leg_volume(example_airwayleg):
    v = example_airwayleg.volume()
    assert isinstance(v, Volume)

def test_airwayleg_volume_wrong_fl_order():
    """
    Ensure max fl is > min fl
    """
    with pytest.raises(ValueError):
        al = AirwayLeg(
        upper_limit_fl=200,
        lower_limit_fl=400,
        p0=Pos2D(0.,0.),
        p0_identifier="FIX1",
        p1=Pos2D(1.,0.),
        p1_identifier="FIX2"
        )
        v = al.volume()


def test_airway_init_idonly():
    """
    Instantiate using just an identifier
    """
    a = Airway(identifier="id1")
    assert isinstance(a, Airway)


def test_airway_init_id_and_legs():
    """
    Instantiate with identifier and list of legs
    """
    a1 = AirwayLeg(
        upper_limit_fl=400,
        lower_limit_fl=200,
        p0=Pos2D(0.,0.),
        p0_identifier="FIX1",
        p1=Pos2D(1.,0.),
        p1_identifier="FIX2"
    )
    a2 = AirwayLeg(
        upper_limit_fl=400,
        lower_limit_fl=200,
        p0=Pos2D(1.,0.),
        p0_identifier="FIX2",
        p1=Pos2D(2.,0.),
        p1_identifier="FIX3"
    )
    a = Airway("id2", [a1, a2])
    assert isinstance(a, Airway)
    fixes = a.fixes()
    assert fixes == ['FIX1', 'FIX2', 'FIX3']
    coords = a.coords()
    assert isinstance(coords, list)
    assert len(coords) == 3
    for i, coord in enumerate(coords):
        assert isinstance(coord, Pos2D)
        assert coord.lat == float(i)


def test_airway_init_bad_leg_order():
    """
    Test that the fixes() method throws a ValueError
    if the order of fixes is such that the start fix of one leg
    is not the end fix of the previous one.
    """
    a1 = AirwayLeg(
        upper_limit_fl=400,
        lower_limit_fl=200,
        p0=Pos2D(0.,0.),
        p0_identifier="FIX1",
        p1=Pos2D(2.,0.),
        p1_identifier="FIX3"
    )
    a2 = AirwayLeg(
        upper_limit_fl=400,
        lower_limit_fl=200,
        p0=Pos2D(1.,0.),
        p0_identifier="FIX2",
        p1=Pos2D(3.,0.),
        p1_identifier="FIX4"
    )
    a = Airway("id3", [a1, a2])
    with pytest.raises(ValueError):
        fixes = a.fixes()