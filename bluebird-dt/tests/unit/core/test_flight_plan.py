import pytest

from bluebird_dt.core import FlightPlan


def test_data(example_flightplan):
    """
    Test data is returned in correct format.
    """

    flightplan = example_flightplan
    data = flightplan.data()

    assert "route" in data
    assert "unexpanded_route" in data
    assert "origin" in data
    assert "dest" in data
    assert "milcivil" in data
    assert "sector_crossing_seq" in data
    assert "requested_flight_level" in data
    assert "filed_true_airspeed" in data
    assert "assigned_squawk" in data


def test_init_no_args():
    with pytest.raises(TypeError):
        fp = FlightPlan()


def test_to_from_json(example_flightplan):
    serialised_flightplan = example_flightplan.to_json()

    roundtrip = FlightPlan.from_json(serialised_flightplan)

    assert roundtrip.data() == example_flightplan.data()

