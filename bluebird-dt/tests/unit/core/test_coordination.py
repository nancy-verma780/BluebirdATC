import pytest

from bluebird_dt.core import Coordination


@pytest.fixture
def example_coordination_only_required() -> Coordination:
    return Coordination(
        callsign="AIR0", from_sector=None, to_sector=None, fl=300.0, fix="EARTH", direction="Horizontal"
    )


def test_json_roundtrip(example_coordination_only_required: Coordination):
    serialised = example_coordination_only_required.to_json()

    roundtrip = Coordination.from_json(serialised)

    assert roundtrip.data() == example_coordination_only_required.data()
