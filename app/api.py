from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from tortoise import Tortoise

from app import logging
from app.configuration import Configuration
from app.exception_handlers import exception_handler
from app.openid.twitch_jwt import TwitchOidcValidator
from app.routers.oauth import oauth_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configuration = Configuration()
    twitch_validator = TwitchOidcValidator(configuration.twitch_client_id)

    # Configure logging
    logging.configure_logging(configuration.log_level)

    await Tortoise.init(
        db_url=configuration.database_url,
        modules={"models": ["app.models.sql"]},
    )

    app.state.configuration = configuration
    app.state.twitch_validator = twitch_validator

    yield

    await Tortoise.close_connections()


api: FastAPI = FastAPI(lifespan=lifespan)
api.include_router(oauth_router)

api.add_exception_handler(Exception, exception_handler)