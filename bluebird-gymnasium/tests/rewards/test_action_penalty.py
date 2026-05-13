from bluebird_gymnasium.rewards.action_penalty import (
    action_penalty_const,
    action_penalty_thresh,
)


def test_action_penalty_const(gym_env):
    """Test `action_penalty_const` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 1
    assert action_penalty_const(gym_env, callsign, action) == -1.0
    action = 0
    assert action_penalty_const(gym_env, callsign, action) == 0.0


def test_action_penalty_thresh(gym_env):
    """Test `action_penalty_thresh` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 0
    assert action_penalty_thresh(gym_env, callsign, action) == 0.0

    action = 1
    assert action_penalty_thresh(gym_env, callsign, action) <= 0.0
