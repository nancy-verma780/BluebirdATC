# Bluebird Gymnasium

A suite of gymnasium environments for air traffic control (ATC).
The environments are based on [bluebird-dt](https://github.com/project-bluebird/BluebirdATC/tree/main/bluebird-dt) (an ATC simulator).

The environments support research in agent-based learning (e.g. reinforcement learning) for ATC.
It supports either single agent or multi-agents scenarios.

## Installation

The default installation instructions are based on the use of `uv`, a package and dependency manager. However, if you want to perform a `conda` based installation, please visit the [alternate installation instructions](./ALTERNATE_INSTALLATION.md#instructions) which contains installation and steps and how to use the package. 

### Pre-requisites
1. [UV](https://docs.astral.sh/uv/) package and dependency manager. If you do not already have `uv` installed, follow the instructions on the [installation](https://docs.astral.sh/uv/getting-started/installation/) page. We recommend using the official installer option.

### Default Installation Instructions

First, download a copy of the [BluebirdATC](https://github.com/project-bluebird/BluebirdATC/) repository. Either clone the repository using git or just download directly from github web. The repository contains both the `bluebird-dt` (core simulator) and `bluebird-gymnasium` (a gymnasium wrapper around the core simulator) packages.
For example, use the command below to clone the repository.

```bash
git clone https://github.com/project-bluebird/BluebirdATC.git
```

Then, install the `bluebird_gymnasium` using `uv`.

```bash
cd BluebirdATC/bluebird-gymnasium
uv sync --no-dev
```

To contribute to the project's development, use the command below to install `bluebird-gymnasium`. The development dependencies will be installed together with the core dependencies.

```bash
cd BluebirdATC/bluebird-gymnasium
uv sync
```

## Usage

### Basic Usage

bluebird-gymnasium currently supports the following environments/airspace:
X sector, Y sector, I sector, Xplus sector and Springfield sector.

To run any, the `uv` or `conda` environment in which `bluebird-gymnasium` was installed must be activated.
For uv:
```bash
cd BluebirdATC/bluebird-gymnasium
source .venv/bin/activate
```

Please see [alternate basic usage](./ALTERNATE_INSTALLATION.md#usage) for `conda` based set up.

To instantiate a X sector environment with the default config, run:

```bash
python
>>> import gymnasium as gym
>>> import bluebird_gymnasium
>>> env = gym.make("SectorXEnv-v0")
```

## Development

### Contributing

Thank you for your interest in contributing. Please read the contributing guidelines, clone the repository and start development. Open a pull request to submit requested changes to the repository.

### Development Dependencies Installation

To install `bluebird-gymnasium` together with its core and development depedencies, use the command below.

```bash
cd BluebirdATC/bluebird-gymnasium/
uv sync
```

### Tests

To run tests, enter the command below in the terminal/console.
Note that the command should be run in the repository home directory.

```bash
cd BluebirdATC/bluebird-gymnasium/
pytest tests/ -p no:warnings
```

### Documentation

The online documentation for the `bluebird_gymnasium` package can be found by running the command:

```bash
../scripts/docs-serve
```

from this directory, then navigating a web browser to `http://localhost:8010`.

### Bug Reporting

To report a bug, open an issue in the repository.

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
