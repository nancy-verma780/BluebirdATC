import typing

import pytest

from bluebird_gymnasium.envs import ViewType
from bluebird_gymnasium.envs.infinite import CustomInfiniteEnv, InfiniteEnv
from bluebird_gymnasium.envs.sector_i import SectorIEnv
from bluebird_gymnasium.envs.sector_x import SectorXEnv
from bluebird_gymnasium.envs.sector_xplus import SectorXPlusEnv
from bluebird_gymnasium.envs.sector_y import SectorYEnv
from bluebird_gymnasium.envs.springfield import SpringfieldEnv

EnvCls: typing.TypeAlias = typing.Any

SECTOR_ENV_CLASSES = (SectorIEnv, SectorXEnv, SectorXPlusEnv, SectorYEnv)
GENERATED_ENV_CLASSES = (
    InfiniteEnv,
    CustomInfiniteEnv,
    SectorIEnv,
    SectorXEnv,
    SectorXPlusEnv,
    SectorYEnv,
)


def _get_env_instance(env_cls: EnvCls):
    config = env_cls.get_default_env_config(ViewType.CENTRALIZED)

    if env_cls in SECTOR_ENV_CLASSES:
        config.scenario_config["args"]["num_aircraft"] = 4

    return env_cls(config=config)


def _initial_aircraft_signature(gym_env):
    """Build a stable snapshot of generated initial traffic."""

    return tuple(
        (
            callsign,
            aircraft.fl,
            aircraft.lat,
            aircraft.lon,
            aircraft.heading,
            aircraft.speed_tas,
            tuple(aircraft.flight_plan.route.filed),
        )
        for callsign, aircraft in sorted(
            gym_env.get_simulator_env().aircraft.items()
        )
    )


@pytest.mark.parametrize(
    "env_cls", GENERATED_ENV_CLASSES, ids=lambda env_cls: env_cls.__name__
)
def test_reset_seed_controls_generated_aircraft(env_cls: EnvCls):
    """Test that reset seeds are propagated to scenario generation."""

    gym_env = _get_env_instance(env_cls)

    gym_env.reset(seed=42)
    first_seed_signature = _initial_aircraft_signature(gym_env)

    gym_env.reset(seed=43)
    second_seed_signature = _initial_aircraft_signature(gym_env)

    gym_env.reset(seed=42)
    repeated_seed_signature = _initial_aircraft_signature(gym_env)

    assert repeated_seed_signature == first_seed_signature
    assert second_seed_signature != first_seed_signature


def test_reset_seed_does_not_control_springfield_aircraft():
    """Test that fixed-file scenarios are not changed by reset seeds."""

    gym_env = _get_env_instance(SpringfieldEnv)

    gym_env.reset(seed=42)
    first_seed_signature = _initial_aircraft_signature(gym_env)

    gym_env.reset(seed=43)
    second_seed_signature = _initial_aircraft_signature(gym_env)

    assert second_seed_signature == first_seed_signature
