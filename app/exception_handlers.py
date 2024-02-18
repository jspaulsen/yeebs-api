import logging


from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
from app.configuration import Configuration

from app.openid.twitch_jwt import TokenException


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


def token_exception_handler(request: Request, exc: TokenException) -> JSONResponse:
    configuration: Configuration = request.app.state.configuration
    description = exc.description or "Invalid token provided"
    frontend_url = configuration.frontend_url.rstrip("/")
    redirect_url = frontend_url + f"/error?error=invalid_token&error_description={description}"

    return RedirectResponse(
        url=redirect_url,
        status_code=302,
    )

