# Alternate Installation Instructions (Conda-based)

## Instructions

### Pre-requisites
1. `bluebird-gymnasium` requires `bluebird-dt` which comes prepackaged when the parent repository [BluebirdATC](https://github.com/project-bluebird/BluebirdATC/) is downloaded or cloned. Both codebases are at the same directory level (see below).

```text
├── bluebird-dt/
│   ├── README.md
│   └── ...
├── bluebird-gymnasium/
    ├── README.md
    └── ...
```

2. [UV](https://docs.astral.sh/uv/) package and dependency manager. If you do not already have `uv` installed, follow the instructions on the [installation](https://docs.astral.sh/uv/getting-started/installation/) page. We recommend using the official installer option.

Next, enter the following instructions in the terminal.

```bash
git clone https://github.com/project-bluebird/BluebirdATC.git 
conda create -n bluebird_gymnasium python=3.13
conda activate bluebird_gymnasium
cd bluebird_gymnasium/
pip install -r requirements.txt
pip install -e .
```

## Usage

### Basic Usage

bluebird-gymnasium currently supports the following environments/airspace:
X sector, Xplus sector, Y sector and I sector.

For conda:
```
conda activate bluebird_gymnasium
```

To instantiate a X sector environment with the default config, run:

```bash
python
>>> import gymnasium as gym
>>> import bluebird_gymnasium
>>> env = gym.make("SectorXEnv-v0")
```

## Sample RL Agents

A sample agent that takes random actions.

```bash
import gymnasium as gym
import bluebird_gymnasium

env = gym.make("SectorXEnv-v0")
obs, info = env.reset()
done = False

while not done:
    action = env.action_space.sample()
    obs, reward, done, truncated, info = env.step(action)
```

