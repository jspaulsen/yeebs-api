import os

from docker import DockerClient
# from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from tortoise import Tortoise


os.environ["DATABASE_URL"] = "postgres://test_user:test_pass@localhost:5432/database"
os.environ["LOG_LEVEL"] = "DEBUG"
os.environ["TWITCH_CLIENT_ID"] = "test_client_id"
os.environ["TWITCH_CLIENT_SECRET"] = "test_client_secret"


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
            container.stop()
            container.remove()
        
        for network in networks:
            network.remove()


@pytest_asyncio.fixture
async def setup_tortoise(setup_database):
    await Tortoise.init(
        db_url=setup_database,
        modules={"models": ["app.models.sql"]},
    )