# Source code reference

## Environments

::: bluebird_gymnasium.envs
    options:
      docstring_style: google
      members:
        - BaseEnv
        - SectorIEnv
        - SectorXEnv
        - SectorXPlusEnv
        - SectorYEnv
        - SpringfieldEnv
        - get_default_config
        - get_env_cls_and_config
      show_source: false

## Actions

::: bluebird_gymnasium.actions
    options:
      docstring_style: google
      members:
        - ActionParser
        - ACTION_NOOP
        - NUM_NOOP_ACTIONS
        - DEFAULT_RELATIVE_HEADING
        - DEFAULT_RELATIVE_CLIMB_DESCENT
        - DEFAULT_RELATIVE_SPEED
        - DEFAULT_ROUTE_DIRECT
        - registry_actions
      show_source: false

## Rewards

::: bluebird_gymnasium.rewards
    options:
      docstring_style: google
      members:
        - registry_reward_fn
        - action_penalty_memory
        - action_penalty_const
        - action_penalty_thresh
        - expeditious_const
        - expeditious_linear
        - expeditious_quad
        - expeditious_exp
        - safety_simple_avoidance_exp
        - safety_simple_avoidance_nvl
        - conflict_resolution_exp
        - conflict_resolution_tanh
        - reward_drlan
      show_source: false

## State Representation

::: bluebird_gymnasium.state_repr
    options:
      docstring_style: google
      members:
        - BaseRepresentation
        - FullRepresentation
        - FullRepresentationRaw
        - MinimalRepresentation
        - MinimalRepresentationRaw
        - RelativeRepresentation
        - RelativeRepresentationRaw
        - VanillaRepresentation
        - VanillaRepresentationRaw
        - DrlanRepresentation
        - DrlanRepresentationRaw
        - registry_repr
      show_source: false

## Wrappers

::: bluebird_gymnasium.wrappers.trajectory_overlay
    options:
      docstring_style: google
      show_source: false

## Utilities

::: bluebird_gymnasium.utils
    options:
      docstring_style: google
      members:
        - TURN_DIR_LEFT
        - TURN_DIR_RIGHT
        - TURN_DIR_NO_TURN
        - TECHNICAL_SAFETY_LATERAL_SEPARATION
        - TECHNICAL_SAFETY_VERTICAL_SEPARATION
        - MAX_SPEED_TAS
      show_source: false
