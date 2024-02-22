import asyncio
import os
import time
import uuid

from docker import DockerClient
# from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from tortoise import Tortoise

from app.models.sql.user import User


os.environ["DATABASE_URL"] = "postgres://test_user:test_pass@localhost:5432/database"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["TWITCH_CLIENT_ID"] = "test_client_id"
os.environ["TWITCH_CLIENT_SECRET"] = "test_client_secret"
os.environ['AES_ENCRYPTION_KEY'] = '5d70a2b6386db77d88c4b7be20ccf37a'
os.environ['JWT_SECRET_KEY'] = '5d70a2b6386db77d88c4b7be20ccf37a'


@pytest.fixture(scope="session")
def setup_database():
    client = DockerClient.from_env()
    containers = []
    networks = []

    existing_containers = client.containers.list(
        all=True,
        filters={
            "name": [
                "postgres_test", 
                "dbmate_test", 
            ],
        },
    )

    existing_networks = client.networks.list(
        filters={
            "name": "pytest_network",
        },
    )

    for container in existing_containers:
        container.stop()
        container.remove()

    for network in existing_networks:
        network.remove()

    try:
        network = client.networks.create("pytest_network")
        networks.append(network)

        pg_container = client.containers.run(
            "postgres:16",
            detach=True,
            name="postgres_test",
            environment={
                "POSTGRES_USER": "test_user",
                "POSTGRES_PASSWORD": "test_pass",
                "POSTGRES_DB": "database",
            },
            network="pytest_network",
            healthcheck={"test": "pg_isready -U test_user -h ", "interval": 1000000},
            ports={"5432/tcp": 5432},
        )

        containers.append(pg_container)

        dbmate_container = client.containers.run(
            "amacneil/dbmate",
            command="--wait up",
            detach=True,
            name="dbmate_test",
            environment={
                "DATABASE_URL": "postgres://test_user:test_pass@postgres_test:5432/database?sslmode=disable"
            },
            network="pytest_network",
            volumes={
                os.path.abspath("./db/migrations"): {
                    "bind": "/db/migrations",
                    "mode": "ro",
                }
            },
        )

        containers.append(dbmate_container)

        # Wait for dbmate to finish running migrations
        result = dbmate_container.wait(timeout=30)

        if result["StatusCode"] != 0:
            logs = (
                dbmate_container
                    .logs()
                    .decode()
            )

            raise RuntimeError(f"Dbmate failed to run up migrations with status code {result['StatusCode']}. Logs: {logs}")
        
        yield os.environ["DATABASE_URL"]
    finally:
        for container in containers:
            container.remove(force=True)
        
        for network in networks:
            network.remove()


@pytest_asyncio.fixture(scope="session")
async def setup_tortoise(setup_database):
    await Tortoise.init(
        db_url=setup_database,
        modules={"models": ["app.models.sql"]},
    )


@pytest_asyncio.fixture
async def setup_user(setup_tortoise):
    user = await User.create(
        username="test_user",
        external_user_id=str(uuid.uuid4()),
    )

    yield user
    await user.delete()


# Required for pytest-asyncio to work 
# with Tortoise / running async tests simultaneously
@pytest.yield_fixture(scope="session")
def event_loop(request):
    loop = (
        asyncio
            .get_event_loop_policy()
            .new_event_loop()
    )

    yield loop

    loop.close()
