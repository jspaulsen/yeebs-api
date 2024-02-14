from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from tortoise import Tortoise


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await Tortoise.init(
        db_url="postgres://postgres:example@postgres:5432/postgres",
        modules={"models": ["app.models.sql"]},
    )
    # await Tortoise.init() # TODO: Once setup, use this

    yield

    # await Tortoise.close_connections()


api = FastAPI(lifespan=lifespan)

    # register_tortoise example
    # @app.on_event("startup")
    # async def init_orm() -> None:  # pylint: disable=W0612
    #     await Tortoise.init(config=config, config_file=config_file, db_url=db_url, modules=modules)
    #     logger.info("Tortoise-ORM started, %s, %s", connections._get_storage(), Tortoise.apps)
    #     if generate_schemas:
    #         logger.info("Tortoise-ORM generating schema")
    #         await Tortoise.generate_schemas()

    # @app.on_event("shutdown")
    # async def close_orm() -> None:  # pylint: disable=W0612
    #     await connections.close_all()
    #     logger.info("Tortoise-ORM shutdown")

    # if add_exception_handlers:

    #     @app.exception_handler(DoesNotExist)
    #     async def doesnotexist_exception_handler(request: Request, exc: DoesNotExist):
    #         return JSONResponse(status_code=404, content={"detail": str(exc)})

    #     @app.exception_handler(IntegrityError)
    #     async def integrityerror_exception_handler(request: Request, exc: IntegrityError):
    #         return JSONResponse(
    #             status_code=422,
    #             content={"detail": [{"loc": [], "msg": str(exc), "type": "IntegrityError"}]},
    #         )
