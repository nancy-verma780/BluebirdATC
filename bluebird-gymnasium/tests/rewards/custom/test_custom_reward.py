from bluebird_gymnasium.rewards.custom.custom_reward import custom_reward_fn


def test_custom_reward_fn(gym_env):
    """Test `custom_reward_fn` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    action = 0
    # this function returns zero until it is implemented
    assert custom_reward_fn(gym_env, callsign, action) == 0.0
