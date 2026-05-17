# BluebirdATC
A Digital Twin for use in ATC simulations, and a training environment for AI agents.

This repository contains the following packages:
 * `bluebird-dt` - the digital twin.  See [here](bluebird-dt/README.md) for more information.
 * `bluebird-api` - A REST api for the digital twin.  See [here](bluebird-api/README.md) for more information.
 * `bluebird-gymnasium` - a gym environment for reinforcement learning agents.  See [here](bluebird-gymnasium/README.md) for more details.
 * `bluebird-hmi` - an optional web-based visualisation package.  See [here](bluebird-hmi/README.md) for details.

## Documentation

To build the full web-based docs, run the following command from this directory: 
```
./scripts/docs-serve
```
then navigate your browser to [here](http://localhost:8010).

## Getting started

We recommend the Jupyter notebooks in the `examples/` directories of `bluebird-dt` (for core Digital Twin use) or `bluebird-gymnasium` (for Agent development).   To run these, change to the `examples/` directory and run the command:
```
uv run jupyter notebook
```

## (AI)r traffic controller challenge
Information relating to the (AI)r traffic controller challenge can be found in the `competition` folder. See the `Competition-Intro.ipynb` notebook to get started with the competition specific setup.

## Contributing

Please see the guidelines [here](CONTRIBUTING.md) if you would like to contribute to BluebirdATC.