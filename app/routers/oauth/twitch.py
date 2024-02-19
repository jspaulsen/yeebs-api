import logging

from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse
import pendulum

from app.clients.twitch import TwitchClient
from app.configuration import Configuration
from app.access_token_manager import AccessTokenManager
from app.models.sql.authorization_token import AuthorizationToken, Origin
from app.models.sql.user import User
from app.openid.twitch_jwt import TwitchOidcValidator

from app.routers.oauth import oauth_router


logger = logging.getLogger(__name__)



@oauth_router.get("/twitch/callback")
async def twitch_oauth_callback(
    request: Request,
    code: str | None = None, 
    error: str | None = None,
    error_description: str | None = None,
) -> JSONResponse:
    configuration: Configuration = request.app.state.configuration
    validator: TwitchOidcValidator = request.app.state.twitch_validator
    token_manager: AccessTokenManager = request.app.state.token_manager

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
        jwt = validator.validate_jwt(token.id_token)

        # Create or update the user with the new token
        user = await User.get_or_none(external_user_id=jwt.sub)
        now = pendulum.now("utc")

        if not user:
            user = await User.create(
                external_user_id=jwt.sub,
                created_at=now,
                updated_at=now,
            )
        
        user.updated_at = now
        await user.save()

        # Find an authorization token for the user; if it doesn't exist, create one
        auth_token = await AuthorizationToken.get_or_none(user_id=user.id)

        if not auth_token:
            auth_token = await AuthorizationToken.create(
                user=user,
                refresh_token=token.refresh_token,
                origin=Origin.Twitch,
                expires_at=pendulum.now("utc").add(days=29) # https://dev.twitch.tv/docs/authentication/refresh-tokens/#refresh-token-lifecycle
            )

        auth_token.refresh_token = token.refresh_token
        await auth_token.save()

        # Set the cookie for the user
        response.set_cookie(
            "access_token",
            token.access_token,
            max_age=token.expires_in,
            httponly=True,
            secure=True,
            samesite="strict",
        )

        token_manager.add_access_token(
            "twitch",
            user.external_user_id,
            token,
        )
    
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