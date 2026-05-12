# `bluebird_gymnasium` documentation

A suite of [gymnasium](https://github.com/Farama-Foundation/Gymnasium) API compliant environments for air traffic control (ATC).
The environments are based on the digital twin simulator, [bluebird-dt](https://github.com/project-bluebird/BluebirdATC/bluebird-dt), serving as a wrapper around it. The environments support research in learning-based agents (e.g., reinforcement learning and imitation learning) for ATC. It supports either single agent (aka centralized) or multi-agent (aka decentralized) agent set up.

In addition to the environment specification, the package also contains a set of state spaces (encodings), reward functions, and discrete action spaces definitions that are configurable, thus enabling users to set up custom problems according to their defined specifications. Furthermore, users develop new reward functions. See [Rewards](rewards) for more information.

## Installation

For installation instructions, please see the [README.md](https://github.com/project-bluebird/BluebirdATC/tree/HEAD/bluebird-gymnasium) in the project's repository.

## Simple usage

To instantiate an environment in the suite, for example, the X sector environment, enter the commands below (after the installation and activation of the virtual environment).

```python
$ python
>>> import gymnasium as gym
>>> import bluebird_dt
>>> env = gym.make("SectorXEnv-v0")
```

For more details, please see the Getting started section below.

## Getting started

Start with the `Examples` tab in these docs for rendered notebook walkthroughs of the use of the `bluebird_gymnasium`, setting up environments and using a sample agent. The source notebooks remain in bluebird-gymnasium/examples if you want to run or edit them locally.
