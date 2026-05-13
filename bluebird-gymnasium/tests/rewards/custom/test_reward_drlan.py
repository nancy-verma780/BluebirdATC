from bluebird_gymnasium.rewards.custom.reward_drlan import reward_drlan


def test_reward_drlan(gym_env):
    """Test `reward_drlan` reward function."""

    tracked_aircraft = gym_env.get_tracked_aircraft_data()
    callsign = list(tracked_aircraft.keys())[0]

    # for single aircraft env with noop action taken, a small
    # negative reward is expected.
    action = 0
    assert reward_drlan(gym_env, callsign, action) <= 0.0
