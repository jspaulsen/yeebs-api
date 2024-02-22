import logging

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
import pendulum

from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.services.authorization import Authorization
from app.models.sql.authorization_token import Origin
from app.models.sql.user import User

from app.routers.oauth import oauth_router
from app.services.identity import Identity


logger = logging.getLogger(__name__)



@oauth_router.get("/twitch/callback")
async def twitch_oauth_callback(
    request: Request,
    code: str | None = None, 
    error: str | None = None,
    error_description: str | None = None,
) -> JSONResponse:
    configuration: Configuration = request.app.state.configuration
    token_manager: Authorization = request.app.state.token_manager
    identity: Identity = request.app.state.identity

    client = TwitchClient(
        configuration.twitch_client_id, 
        configuration.twitch_client_secret,
    )

    redirect_uri = configuration.redirect_host + "/oauth/twitch/callback"
    frontend_url = configuration.frontend_url.rstrip("/")

    response = RedirectResponse(
        url=frontend_url,
        status_code=303,
    )

    if not code and not error:
        return JSONResponse(status_code=400, content={"error": "Invalid request"})
    
    if error or not code:
        error = error or "Invalid request"

        # If the user denied access, we should return a 400
        if error != "access_denied":
            logger.info(
                f"An error occurred during the Twitch OAuth callback: {error}",
                extra={
                    "error": error
                },
            )

        if error_description:
            error = f"{error}: {error_description}"
        
        response = RedirectResponse(
            url=frontend_url + f"/error?error={error}&error_description={error_description}",
            status_code=302,
        )
    
    else: # If we're given a code, we should exchange it for a token
        token = await client.exchange_code_for_token(redirect_uri, code)
        token_validation = await client.validate_token(token.access_token)

        # Retrieve user information from token
        external_user_id = token_validation.user_id
        username = token_validation.login

        # Create the user if they don't exist
        user = await User.get_or_none(external_user_id=external_user_id)

        if not user:
            user = await User.create(
                external_user_id=external_user_id,
                username=username,
            )

        # Add the access token to the database
        await token_manager.upsert_access_token(Origin.Twitch, user.id, token)

        # Need to generate a JWT for the user
        # This will be used to authenticate the user in the frontend
        # TODO: This changes,
        # Set the cookie for the user
        # response.set_cookie(
        #     "access_token",
        #     our_access_token,
        #     max_age=600, # TODO
        #     httponly=True,
        #     secure=True,
        #     samesite="strict",
        # )
    
    return response


@oauth_router.get("/twitch/redirect")
async def twitch_oauth_redirect(request: Request) -> RedirectResponse:
    configuration: Configuration = request.app.state.configuration
    redirect_uri = configuration.redirect_host + "/oauth/twitch/callback"
    scope = "+".join(configuration.twitch_scope)

    twitch_redirect_url = (
        "https://id.twitch.tv/oauth2/authorize" +
        f"?response_type=code" +
        f"&client_id={request.app.state.configuration.twitch_client_id}" +
        f"&redirect_uri={redirect_uri}" +
        f"&scope={scope}"
    )

    return RedirectResponse(url=twitch_redirect_url)