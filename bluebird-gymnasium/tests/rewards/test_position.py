from bluebird_gymnasium.rewards.position import (
    position_status_const,
)


def test_position_status_const(gym_env):
    """Test `position_status_const` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 0
    assert position_status_const(gym_env, callsign, action) == 0.0
