import logging


from fastapi import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


def exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "An unhandled exception occurred",
        exc_info=exc,
        stack_info=True
    )

    return JSONResponse(
        status_code=500, 
        content={"error": "Internal server error"}
    )
