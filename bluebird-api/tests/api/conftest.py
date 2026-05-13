import asyncio
import pytest
from fastapi.testclient import TestClient
import datetime

from bluebird_api import app
from bluebird_api.runner import Runner
from bluebird_api.models import RunnerStore


@pytest.fixture(scope="module")
def runner():
    runner = Runner("Springfield", "testScenario")

    # Mock the function delete doing nothing
    runner.delete = lambda: asyncio.sleep(0)

    return runner

@pytest.fixture(scope="module")
def sector_id():
    return "test_sector"

@pytest.fixture
def callsign():
    return "AIR01"
    
@pytest.fixture(scope="module")
def client():
    """
    Fixture to create a TestClient instance for testing
    """
    return TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup(client):
    """
    Load scenario before running test if not currently loaded.
    Allow an opt-out for the occasional test which specifically tests prior to load
    """
    if not client.get("/status").json().get("exists"):
        client.post("/load/Springfield/testScenario")

@pytest.fixture()
def tear_down():
    if RunnerStore.current_runner is not None:
        try:
            asyncio.run(RunnerStore.current_runner.delete())
        except Exception:
            pass
        finally:
            RunnerStore.current_runner = None
    yield

@pytest.fixture
def mock_save_sim(monkeypatch):
    """
    Prevent save files being created
    """

    async def mock_save():
        return True

    monkeypatch.setattr("bluebird_api.routers.core.save", mock_save)


@pytest.fixture
def mock_evolve(monkeypatch):
    """
    Prevent simulation being evolved
    """

    async def mock_evolve(arg1, arg2):
        return True

    monkeypatch.setattr("bluebird_api.routers.core.evolve", mock_evolve)


@pytest.fixture
def mock_filter_log_list(monkeypatch):
    """
    Prevent the API trying to load logs which might not exist.
    """

    def mock(*args):
        return []

    monkeypatch.setattr("bluebird_api.routers.metrics.filter_log_list", mock)
