from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from tortoise import Tortoise

from app import logging
from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.services.authorization import Authorization
from app.exception_handlers import exception_handler
from app.routers.oauth import oauth_router
from app.services.identity import Identity


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configuration = Configuration()
    token_manager = Authorization(configuration)
    identity = Identity(configuration)

    # Configure logging
    logging.configure_logging(configuration.log_level)

    await Tortoise.init(
        db_url=configuration.database_url,
        modules={"models": ["app.models.sql"]},
    )

    app.state.configuration = configuration
    app.state.token_manager = token_manager
    app.state.identity = identity

    # get background tasks
    app.state.background_tasks = []

    yield

    await Tortoise.close_connections()


api: FastAPI = FastAPI(lifespan=lifespan)
api.include_router(oauth_router)

api.add_exception_handler(Exception, exception_handler)