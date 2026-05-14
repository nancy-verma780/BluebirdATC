# Welcome to bluebird-api

The `bluebird-api` package is a FastAPI app that gives access to the `bluebird-dt` digital twin via a REST API.

## Terminology

In this context, **API** means the HTTP interface used by agents and frontends (including the HMI GUI) to interact with a running simulation.

## Using the pre-built API

The API package is part of this repository, so you can run it directly from source without creating a separate service scaffold.

* From the `BluebirdATC/bluebird-api` directory, start the server:

```bash
uv run uvicorn bluebird_api:app --port 8000
```

* Check the root endpoint in your browser: [http://localhost:8000](http://localhost:8000)

* Open the interactive API docs (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs)

* If you also want the GUI, open the HMI served by the API: [http://localhost:8000/hmi](http://localhost:8000/hmi)

## Developer Guide


### Running locally

Run the API service locally:

```bash
cd bluebird-api
uv run uvicorn bluebird_api:app --port 8000
```

### Running tests and checks

Run the API test suite from the package directory:

```bash
cd bluebird-api
uv run pytest tests/
```

To use parallel workers:

```bash
cd bluebird-api
uv run pytest -n auto tests/
```


### Source README

For package-level details, see the source README:

[bluebird-api README](https://github.com/project-bluebird/BluebirdATC/blob/main/bluebird-api/README.md)
