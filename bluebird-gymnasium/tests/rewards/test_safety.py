from bluebird_gymnasium.rewards.safety import (
    safety_simple_avoidance_exp,
    safety_simple_avoidance_nvl,
)


def test_safety_simple_avoidance_exp(gym_env):
    """Test `safety_simple_avoidance_exp` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 0
    assert safety_simple_avoidance_exp(gym_env, callsign, action) <= 0.0


def test_safety_simple_avoidance_nvl(gym_env):
    """Test `safety_simple_avoidance_nvl` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 0
    assert safety_simple_avoidance_nvl(gym_env, callsign, action) <= 0.0
