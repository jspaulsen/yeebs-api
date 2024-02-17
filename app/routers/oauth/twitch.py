import logging
from fastapi import Request, Response

from fastapi.responses import JSONResponse, RedirectResponse
from app.clients.twitch import TwitchClient
from app.configuration import Configuration

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
    client = TwitchClient(
        configuration.twitch_client_id, 
        configuration.twitch_client_secret,
    )

    redirect_uri = configuration.redirect_host + "/oauth/twitch/callback"

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

        # TODO: We could serve a nice template here or pass it onto the frontend with an error
        # just assume www.yeebs.dev/oauth/twitch/callback?error=access_denied or something like that
        return JSONResponse(status_code=400, content={"error": error})

    token = client.exchange_code_for_token(redirect_uri, code)

# {"access_token":"4cu8gpqju5dxfva3f381ye61guyu3w","expires_in":13919,"id_token":"eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjEifQ.eyJhdWQiOiJrZHNoa29pN3F5emRwZG5mdWRmYmFhNzc5dzF2NGMiLCJleHAiOjE3MDgyMTAzMjgsImlhdCI6MTcwODIwOTQyOCwiaXNzIjoiaHR0cHM6Ly9pZC50d2l0Y2gudHYvb2F1dGgyIiwic3ViIjoiMTUzNTc3MTI5IiwiYXpwIjoia2RzaGtvaTdxeXpkcGRuZnVkZmJhYTc3OXcxdjRjIiwicHJlZmVycmVkX3VzZXJuYW1lIjoiQ2FubmliYWxKZWVidXMifQ.sTpuuGebS9ng15dfCUTOU2C3bYNSzv9oaBCfUAmLIGm6v7wO5DyzSGsG4A-1rghrJoSMq9dmihkQC3qD2RuwYxi0W7WXbQGaRy9IOM2xZ4IdjRM-sjdypfhLw33fBSo3N_wFY9Sb6fj-5Ma5q_KZH8QqSb050KXBBXJ3Bc12p98shO-pNnr4M0-8KLo2E219Mho2p5spvaxSvg0TKXTEIBmuez8CjvvjO9WLfs0SbVL2d93nZOilaDRnK8ESJF1xN9cQEbRv0iNp-iFXMiRFhRjw8_rj5j5NEb3pjgYXMq1_txTbFrdKRcV1cl66kg1g3x9cYWG1Bk9IKocAsxrwEg","refresh_token":"vmpm5rpm5waju347gchho2kl3w4uitrbmzwjijlp5vpauhw4kn","scope":["bits:read","channel:read:ads","channel:read:redemptions","openid"],"token_type":"bearer"}

    # TODO: This becomes a redirect to the frontend
    # response = RedirectResponse(
    #     url=configuration.frontend_url,
    #     status_code=303,
    # )

    response = JSONResponse(
        status_code=200, 
        content=token,
    )

    # response.set_cookie(
    #     "twitch_access_token",
    #     token["access_token"],
    #     max_age=token["expires_in"],
    #     httponly=True,
    #     secure=configuration.secure_cookies,
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