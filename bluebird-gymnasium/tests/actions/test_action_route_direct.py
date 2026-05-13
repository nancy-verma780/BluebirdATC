from bluebird_gymnasium.actions.simple.route_direct import route_direct

def test_route_direct(gym_env):
    """Test `route_direct` action function."""

    _sector = gym_env.get_active_airspace_sector()
    tracked_aircraft = gym_env.get_tracked_aircraft_data()

    callsign = list(tracked_aircraft.keys())[0]
    next_fix = tracked_aircraft[callsign].next_fix_fr

    action = route_direct(callsign, gym_env)
    assert action.kind == "route_direct_to"
    assert action.value == next_fix


def test_route_direct_fix_after_next(gym_env):
    """Test `route_direct` action function."""

    _sector = gym_env.get_active_airspace_sector()
    tracked_aircraft = gym_env.get_tracked_aircraft_data()

    callsign = list(tracked_aircraft.keys())[0]
    next_fix = tracked_aircraft[callsign].next_fix_fr

    aircraft = gym_env.get_simulator_env().aircraft[callsign]
    route = aircraft.flight_plan.route.filed
    next_fix_idx = route.index(next_fix)

    # route direct to the fix after the next forward fix
    # `value` is set to 2 for this.
    action = route_direct(callsign, gym_env, value=2)
    fix_after_next_fix = route[next_fix_idx + 1]
    assert action.kind == "route_direct_to"
    assert action.value == fix_after_next_fix
