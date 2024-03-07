import logging
from typing import Annotated

from fastapi import Depends, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
import pendulum
from app.clients.spotify import SpotifyClient

from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.identity.jwt import Jwt, jwt_dependency
from app.services.authorization import Authorization
from app.models.sql.authorization_token import Origin
from app.models.sql.user import User

from app.routers.oauth import oauth_router
from app.services.identity import Identity


logger = logging.getLogger(__name__)


@oauth_router.get("/spotify/redirect")
async def spotify_oauth_redirect(request: Request, _: Annotated[Jwt, Depends(jwt_dependency)]) -> Response:
    configuration: Configuration = request.app.state.configuration
    redirect_uri = configuration.redirect_host + "/oauth/spotify/callback"
    scope = "+".join(configuration.spotify_scope)

    spotify_redirect_url = (
        "https://accounts.spotify.com/authorize" +
        f"?response_type=code" +
        f"&client_id={configuration.spotify_client_id}" +
        f"&redirect_uri={redirect_uri}" +
        f"&scope={scope}"
    )

    return RedirectResponse(url=spotify_redirect_url)


@oauth_router.get("/spotify/callback")
async def spotify_oauth_callback(
    request: Request,
    jwt: Annotated[Jwt, Depends(jwt_dependency)],
    code: str | None = None, 
    error: str | None = None,
    error_description: str | None = None,
) -> JSONResponse:
    configuration: Configuration = request.app.state.configuration
    authorization: Authorization = request.app.state.token_manager
    spotify_client = SpotifyClient(
        configuration.spotify_client_id,
        configuration.spotify_client_secret,
    )

    user_id = jwt.claims.user_id

    if not code and not error:
        return JSONResponse(status_code=400, content={"error": "Invalid request"})
    
    if error or not code:
        error = error or "Invalid request"

        # If the user denied access, we should return a 400
        if error != "access_denied":
            logger.info(
                f"An error occurred during the Spotify OAuth callback: {error}",
                extra={
                    "error": error
                },
            )

        if error_description:
            error = f"{error}: {error_description}"
        
        return JSONResponse(status_code=400, content={"error": error})
    
    token = await spotify_client.exchange_code_for_token(
        configuration.redirect_host + "/oauth/spotify/callback",
        code,
    )

    # Store the token in the database
    # TODO: missing user_id
    await authorization.upsert_access_token(
        Origin.Spotify,
        user_id,
        token,
    )

    # redirect to frontend
    return RedirectResponse(
        url=configuration.frontend_url,
        status_code=302,
    )
        
        # if error or not code:
        #     error = error or "Invalid request"

        #     # If the user denied access, we should return a 400
        #     if error != "access_denied":
        #         logger.info(
        #             f"An error occurred during the Twitch OAuth callback: {error}",
        #             extra={
        #                 "error": error
        #             },
        #         )

        #     if error_description:
        #         error = f"{error}: {error_description}"
            
        #     response = RedirectResponse(
        #         url=frontend_url + f"/error?error={error}&error_description={error_description}",
        #         status_code=302,
        #     )
        
        # else: # If we're given a code, we should exchange it for a token
        #     token = await client.exchange_code_for_token(redirect_uri, code)
        #     token_validation = await client.validate_token(token.access_token)

        #     # Retrieve user information from token
        #     external_user_id = token_validation.user_id
        #     username = token_validation.login

        #     # Create the user if they don't exist
        #     user = await User.get_or_none(external_user_id=external_user_id)

        #     if not user:
        #         user = await User.create(
        #             external_user_id=external_user_id,
        #             username=username,
        #         )

        #     # Add the access token to the database
        #     await token_manager.upsert_access_token(Origin.Twitch, user.id, token)

        #     # Generate an access token for the user
        #     access_token = await identity.create_access_token(user)

        #     response.set_cookie(
        #         "access_token",
        #         access_token.model_dump_json(),
        #         max_age=access_token.expires_in,
        #         httponly=True,
        #         secure=False,
        #     )

        # return response

        
    # configuration: Configuration = request.app.state.configuration
    # token_manager: Authorization = request.app.state.token_manager
    # identity: Identity = request.app.state.identity
